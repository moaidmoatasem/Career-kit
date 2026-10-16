from __future__ import annotations

import argparse
import sys
from pathlib import Path

from apply_kit import __version__, facts, ledger, prompt, truthcheck


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="apply-kit")
    p.add_argument("--version", action="version", version=f"apply-kit {__version__}")
    p.add_argument("--facts", type=Path, default=Path("private/facts.yaml"))
    p.add_argument("--db", type=Path, default=Path("private/applications.db"))
    sub = p.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("tailor", help="print a compact tailoring prompt for Claude")
    t.add_argument("--title", required=True)
    t.add_argument("--company", required=True)
    t.add_argument("--desc-file", type=Path, required=True)
    c = sub.add_parser("check", help="truth-check a tailored CV/cover note against the facts")
    c.add_argument("file", type=Path)
    a = sub.add_parser("add", help="log an application you submitted")
    a.add_argument("--title", required=True)
    a.add_argument("--company", required=True)
    a.add_argument("--url", default="")
    a.add_argument("--source", default="")
    a.add_argument("--cv", default="")
    s = sub.add_parser("status", help="update an application's status")
    s.add_argument("id", type=int)
    s.add_argument("status")
    s.add_argument("--notes", default="")
    sub.add_parser("due", help="list applications needing follow-up")
    f = sub.add_parser("funnel", help="applied -> reply -> interview by source or CV variant")
    f.add_argument("--by", default="source", choices=["source", "cv_variant"])
    args = p.parse_args(argv)
    try:
        if args.cmd == "tailor":
            print(
                prompt.build(
                    facts.load(args.facts),
                    args.title,
                    args.company,
                    args.desc_file.read_text("utf-8"),
                )
            )
            return 0
        if args.cmd == "check":
            issues = truthcheck.check(args.file.read_text("utf-8"), facts.load(args.facts))
            print("\n".join(map(str, issues)) if issues else "apply-kit: truth check passed")
            return 1 if issues else 0
        args.db.parent.mkdir(parents=True, exist_ok=True)
        con = ledger.connect(args.db)
        if args.cmd == "add":
            print(
                f"apply-kit: logged #{ledger.add(con, args.title, args.company, args.url, args.source, args.cv)}"
            )
        elif args.cmd == "status":
            ledger.set_status(con, args.id, args.status, args.notes)
            print("apply-kit: updated")
        elif args.cmd == "due":
            for row in ledger.due(con):
                print(f"#{row[0]} {row[1]} @ {row[2]} (follow up since {row[3]})")
        else:
            for name, n, replies, interviews in ledger.funnel(con, args.by):
                print(f"{name}: applied {n}, replies {replies or 0}, interviews {interviews or 0}")
        return 0
    except (OSError, ValueError) as exc:
        print(f"apply-kit: error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
