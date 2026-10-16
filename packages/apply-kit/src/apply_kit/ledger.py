from __future__ import annotations

import sqlite3
from datetime import date, timedelta
from pathlib import Path

STATUSES = ("applied", "replied", "interview", "offer", "rejected", "ghosted", "withdrawn")
SCHEMA = """CREATE TABLE IF NOT EXISTS applications (
  id INTEGER PRIMARY KEY, title TEXT, company TEXT, url TEXT, source TEXT, cv_variant TEXT,
  applied_on TEXT, status TEXT DEFAULT 'applied', follow_up TEXT, notes TEXT DEFAULT '')"""


def connect(path: Path) -> sqlite3.Connection:
    con = sqlite3.connect(str(path))
    con.execute(SCHEMA)
    return con


def add(
    con, title, company, url="", source="", cv_variant="", today: date | None = None, follow_days=7
) -> int:
    d = today or date.today()
    cur = con.execute(
        "INSERT INTO applications(title,company,url,source,cv_variant,applied_on,follow_up) VALUES (?,?,?,?,?,?,?)",
        (
            title,
            company,
            url,
            source,
            cv_variant,
            d.isoformat(),
            (d + timedelta(days=follow_days)).isoformat(),
        ),
    )
    con.commit()
    return int(cur.lastrowid)


def set_status(con, app_id: int, status: str, notes: str = "") -> None:
    if status not in STATUSES:
        raise ValueError(f"status must be one of {STATUSES}")
    cur = con.execute(
        "UPDATE applications SET status=?, notes=notes||? WHERE id=?",
        (status, f" {notes}".rstrip(), app_id),
    )
    if cur.rowcount == 0:
        raise ValueError(f"no application with id {app_id}")
    con.commit()


def due(con, today: date | None = None) -> list[tuple]:
    d = (today or date.today()).isoformat()
    return con.execute(
        "SELECT id,title,company,follow_up FROM applications WHERE status='applied' AND follow_up<=? ORDER BY follow_up",
        (d,),
    ).fetchall()


def funnel(con, by: str = "source") -> list[tuple]:
    if by not in ("source", "cv_variant"):
        raise ValueError("by must be source or cv_variant")
    return con.execute(
        f"SELECT COALESCE(NULLIF({by},''),'(none)'), COUNT(*), "  # noqa: S608
        "SUM(status IN ('replied','interview','offer')), SUM(status IN ('interview','offer')) "
        f"FROM applications GROUP BY 1 ORDER BY 2 DESC"
    ).fetchall()
