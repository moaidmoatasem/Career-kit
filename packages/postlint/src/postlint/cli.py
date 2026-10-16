from __future__ import annotations

import argparse
import sys
from pathlib import Path

from postlint import __version__, config, post, report
from postlint.finding import Finding
from postlint.rules import confidential, pdf, text


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="postlint", description="Lint LinkedIn posts and PDF decks.")
    p.add_argument("--version", action="version", version=f"postlint {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("check", help="lint a post file (and optionally its PDF)")
    c.add_argument("post", type=Path)
    c.add_argument("--pdf", type=Path)
    c.add_argument("--blocklist", type=Path)
    c.add_argument("--config", type=Path)
    c.add_argument("--format", choices=["text", "json"], default="text")

    s = sub.add_parser("scrub", help="write a copy of a PDF with metadata removed")
    s.add_argument("pdf", type=Path)
    s.add_argument("-o", "--output", type=Path, required=True)
    return p


def _check(args: argparse.Namespace) -> int:
    cfg = config.load(args.config)
    parsed = post.parse(args.post.read_text(encoding="utf-8"))
    bl_path = args.blocklist or cfg.blocklist_path
    blocklist = confidential.load_blocklist(bl_path) if bl_path else []

    findings: list[Finding] = []
    findings += text.check_text(parsed.body, cfg)
    findings += confidential.check_blocklist(parsed.body, blocklist, "PL005", "body")
    findings += confidential.check_sensitive_patterns(parsed.body)
    if args.pdf:
        findings += pdf.check_pdf(args.pdf, cfg, blocklist)

    render = report.render_json if args.format == "json" else report.render_text
    print(render(findings))
    return report.exit_code(findings)


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.cmd == "check":
            return _check(args)
        pdf.scrub(args.pdf, args.output)
        print(f"postlint: wrote {args.output}")
        return 0
    except (OSError, ValueError) as exc:
        print(f"postlint: error: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001 - unreadable/corrupt PDFs raise pypdf-specific errors
        print(f"postlint: error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
