from __future__ import annotations

import csv
import sqlite3
from datetime import date, timedelta
from pathlib import Path


def _sum(con: sqlite3.Connection, start: date, end: date) -> tuple[int, int, int]:
    row = con.execute(
        "SELECT COALESCE(SUM(impressions),0), COALESCE(SUM(engagements),0), "
        "COALESCE(SUM(new_followers),0) FROM daily WHERE day>=? AND day<=?",
        (start.isoformat(), end.isoformat()),
    ).fetchone()
    return int(row[0]), int(row[1]), int(row[2])


def _delta(cur: int, prev: int) -> str:
    if prev == 0:
        return "n/a"
    return f"{(cur - prev) / prev * 100:+.0f}%"


def load_pillars(path: Path | None) -> dict[str, str]:
    if not path or not path.is_file():
        return {}
    with path.open(encoding="utf-8", newline="") as fh:
        return {r["url"].strip(): r["pillar"].strip() for r in csv.DictReader(fh)}


def weekly_report(con: sqlite3.Connection, end: date, pillars: dict[str, str] | None = None) -> str:
    cur = _sum(con, end - timedelta(days=6), end)
    prev = _sum(con, end - timedelta(days=13), end - timedelta(days=7))
    rate = f"{cur[1] / cur[0] * 100:.1f}%" if cur[0] else "n/a"
    lines = [
        f"# LinkedIn weekly report (week ending {end.isoformat()})",
        f"- Impressions: {cur[0]} ({_delta(cur[0], prev[0])} vs prior week)",
        f"- Engagements: {cur[1]} ({_delta(cur[1], prev[1])}); engagement rate {rate}",
        f"- New followers: {cur[2]} ({_delta(cur[2], prev[2])})",
    ]
    best = con.execute(
        "SELECT url, impressions FROM posts WHERE impressions IS NOT NULL "
        "ORDER BY impressions DESC LIMIT 1"
    ).fetchone()
    if best:
        lines.append(f"- Top post: {best[0]} ({best[1]} impressions)")
    if pillars:
        agg: dict[str, int] = {}
        for url, imp in con.execute("SELECT url, impressions FROM posts"):
            if url in pillars and imp:
                agg[pillars[url]] = agg.get(pillars[url], 0) + imp
        if agg:
            top = max(agg, key=lambda k: agg[k])
            lines.append(f"- Best pillar by impressions: {top} ({agg[top]})")
    return "\n".join(lines)
