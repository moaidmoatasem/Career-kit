from __future__ import annotations

import argparse
import sys
from pathlib import Path

from bawsala_feeds import __version__, runner


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="bawsala-feeds")
    p.add_argument("--version", action="version", version=f"bawsala-feeds {__version__}")
    p.add_argument("--config", type=Path, default=Path("config.yaml"))
    p.add_argument("--out", type=Path, default=Path("out"))
    args = p.parse_args(argv)
    try:
        jobs = runner.run(args.config, args.out)
    except (OSError, ValueError) as exc:
        print(f"bawsala-feeds: error: {exc}", file=sys.stderr)
        return 2
    print(f"bawsala-feeds: {len(jobs)} jobs -> {args.out}/jobs.csv, shortlist.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
