from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

from li_metrics import __version__, db, ingest, report


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="li-metrics")
    p.add_argument("--version", action="version", version=f"li-metrics {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)
    i = sub.add_parser("ingest", help="load a LinkedIn analytics .xlsx export")
    i.add_argument("xlsx", type=Path)
    i.add_argument("--db", type=Path, default=Path("li-metrics.db"))
    r = sub.add_parser("report", help="print the weekly Markdown report")
    r.add_argument("--db", type=Path, default=Path("li-metrics.db"))
    r.add_argument("--end", type=date.fromisoformat, default=None, help="week ending YYYY-MM-DD")
    r.add_argument("--pillars", type=Path, help="CSV with columns url,pillar")
    args = p.parse_args(argv)
    try:
        if args.cmd == "ingest":
            con = db.connect(args.db)
            counts = ingest.ingest(args.xlsx, con)
            print(f"li-metrics: ingested {counts['daily']} daily rows, {counts['posts']} posts")
            return 0
        con = db.connect(args.db)
        end = args.end or date.today()
        print(report.weekly_report(con, end, report.load_pillars(args.pillars)))
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"li-metrics: error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
