"""线索库：本地 SQLite。每条线索一行，原文正文也存下来，核实时要用。"""
import hashlib, json, sqlite3
from datetime import datetime

from . import config

SCHEMA = """
create table if not exists leads (
  id text primary key,
  url text unique,
  source_id text,
  published text,
  fetched_at text,
  kind text,
  is_roundup integer default 0,
  name text,
  suburb text,
  region text,
  opened_date text,
  event_dates text,
  image_url text,
  image_credit text,
  venue_website text,
  data text,
  article_text text,
  status text default 'new',     -- new / used / rejected / out_of_area
  used_in_issue integer
);
create index if not exists idx_status on leads(status);
"""


def connect():
    db = sqlite3.connect(config.data_dir() / "leads.sqlite")
    db.row_factory = sqlite3.Row
    db.executescript(SCHEMA)
    return db


def lead_id(url: str) -> str:
    return hashlib.sha1(url.encode()).hexdigest()[:12]


def seen(db, url: str) -> bool:
    return db.execute("select 1 from leads where url=?", (url,)).fetchone() is not None


def save(db, row: dict):
    row = dict(row)
    row.setdefault("id", lead_id(row["url"]))
    row.setdefault("fetched_at", datetime.now().isoformat(timespec="seconds"))
    for k in ("data", "event_dates"):
        if k in row and not isinstance(row[k], str):
            row[k] = json.dumps(row[k], ensure_ascii=False)
    cols = ",".join(row)
    q = ",".join("?" for _ in row)
    db.execute(f"insert or replace into leads ({cols}) values ({q})", list(row.values()))
    db.commit()


def as_dict(r) -> dict:
    d = dict(r)
    for k in ("data", "event_dates"):
        if d.get(k):
            d[k] = json.loads(d[k])
    return d


def candidates(db) -> list:
    return [as_dict(r) for r in db.execute("select * from leads where status='new' and region is not null")]


def get(db, lid: str) -> dict:
    r = db.execute("select * from leads where id=?", (lid,)).fetchone()
    return as_dict(r) if r else None


def mark_used(db, ids, issue_no):
    db.executemany("update leads set status='used', used_in_issue=? where id=?", [(issue_no, i) for i in ids])
    db.commit()
