from __future__ import annotations

import csv
from pathlib import Path

from bawsala_feeds.model import Job


def write_csv(jobs: list[Job], path: Path) -> None:
    rows = [j.to_row() for j in jobs]
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def write_shortlist(jobs: list[Job], path: Path, top: int = 15) -> None:
    """Small, token-cheap file for Claude: no descriptions, one line per job."""
    lines = [f"# Shortlist (top {top})", ""]
    for i, j in enumerate(jobs[:top], 1):
        flag = " [visa]" if j.visa_sponsorship else ""
        lines.append(
            f"{i}. **{j.title}** - {j.company} - {j.location or 'n/a'}{flag} "
            f"(score {j.score:g}; {', '.join(j.score_reasons[:4])}) {j.url}"
        )
    lines += ["", "_" + " | ".join(sorted({j.attribution for j in jobs[:top]})) + "_"]
    path.write_text("\n".join(lines), encoding="utf-8")
