from __future__ import annotations

import re
from pathlib import Path

from pypdf import PdfReader, PdfWriter

from postlint.config import Config
from postlint.finding import ERROR, WARNING, Finding
from postlint.rules.confidential import check_blocklist

META_KEYS = ("/Author", "/Title", "/Creator", "/Producer", "/Subject", "/Keywords")


def check_pdf(
    path: Path, cfg: Config, blocklist: list[tuple[str, re.Pattern[str]]]
) -> list[Finding]:
    out: list[Finding] = []
    where = path.name
    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb > cfg.max_pdf_mb:
        msg = f"PDF is {size_mb:.1f} MB (max {cfg.max_pdf_mb})"
        out.append(Finding("PL101", ERROR, msg, where))

    reader = PdfReader(str(path))
    pages = reader.pages
    if len(pages) > cfg.max_pages:
        out.append(
            Finding("PL102", WARNING, f"{len(pages)} pages (aim for <= {cfg.max_pages})", where)
        )

    sizes = {(round(float(p.mediabox.width)), round(float(p.mediabox.height))) for p in pages}
    if len(sizes) > 1:
        out.append(Finding("PL103", ERROR, f"Mixed page sizes: {sorted(sizes)}", where))

    meta = reader.metadata or {}
    present = [k.lstrip("/") for k in META_KEYS if str(meta.get(k, "")).strip()]
    if reader.xmp_metadata is not None:
        present.append("XMP")
    if present:
        out.append(
            Finding(
                "PL104",
                ERROR,
                f"PDF metadata present: {', '.join(present)} (fix: postlint scrub)",
                where,
            )
        )

    if blocklist:
        text = "\n".join((p.extract_text() or "") for p in pages)
        out.extend(check_blocklist(text, blocklist, "PL105", where))
    return out


def scrub(src: Path, dst: Path) -> None:
    """Copy pages into a fresh PDF with all document metadata blanked (no XMP)."""
    reader = PdfReader(str(src))
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    writer.add_metadata({k: "" for k in META_KEYS})
    with dst.open("wb") as fh:
        writer.write(fh)
