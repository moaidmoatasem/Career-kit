from __future__ import annotations

import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS daily (
  day TEXT PRIMARY KEY, impressions INTEGER, engagements INTEGER, new_followers INTEGER);
CREATE TABLE IF NOT EXISTS posts (
  url TEXT PRIMARY KEY, post_date TEXT, impressions INTEGER, engagements INTEGER);
"""


def connect(path: Path | str) -> sqlite3.Connection:
    con = sqlite3.connect(str(path))
    con.executescript(SCHEMA)
    return con


def upsert_daily(con: sqlite3.Connection, day: str, values: dict[str, int]) -> None:
    """Idempotent: only columns present in `values` are overwritten."""
    con.execute("INSERT OR IGNORE INTO daily(day) VALUES (?)", (day,))
    for col, val in values.items():
        if col not in {"impressions", "engagements", "new_followers"}:
            raise ValueError(col)
        con.execute(f"UPDATE daily SET {col}=? WHERE day=?", (val, day))  # noqa: S608


def upsert_post(con: sqlite3.Connection, url: str, post_date: str | None, values: dict) -> None:
    con.execute(
        "INSERT INTO posts(url, post_date, impressions, engagements) VALUES (?,?,?,?) "
        "ON CONFLICT(url) DO UPDATE SET post_date=COALESCE(excluded.post_date, post_date), "
        "impressions=COALESCE(excluded.impressions, impressions), "
        "engagements=COALESCE(excluded.engagements, engagements)",
        (url, post_date, values.get("impressions"), values.get("engagements")),
    )
