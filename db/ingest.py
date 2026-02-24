#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Iterable, Tuple

import mysql.connector


def parse_iso_to_mysql_dt(ts: str) -> datetime:
    """
    Convert ISO-8601 string to timezone-aware datetime in UTC,
    then return naive datetime suitable for MySQL DATETIME (assumed UTC).
    """
    # Handle Z suffix
    ts = ts.replace("Z", "+00:00")
    dt = datetime.fromisoformat(ts)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    dt_utc = dt.astimezone(timezone.utc)
    return dt_utc.replace(tzinfo=None)  # store as UTC naive


def getenv_required(name: str) -> str:
    v = os.getenv(name)
    if not v:
        raise SystemExit(f"Missing required env var: {name}")
    return v


def read_jsonl(path: str) -> Iterable[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


INSERT_SQL = """
INSERT INTO events
(ts, source, event_type, ip, username, status, method, path, http_status, user_agent, host, raw, extra)
VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
"""


def event_to_row(ev: Dict[str, Any]) -> Tuple[Any, ...]:
    ts = parse_iso_to_mysql_dt(ev["timestamp"])
    source = ev.get("source")
    event_type = ev.get("event_type")

    ip = ev.get("ip")
    username = ev.get("username")
    status = ev.get("status")
    method = ev.get("method")
    path = ev.get("path")
    http_status = ev.get("http_status")
    user_agent = ev.get("user_agent")
    host = ev.get("host")
    raw = ev.get("raw")

    # Anything not part of the core columns can go into extra
    core_keys = {
        "timestamp","source","event_type","ip","username","status","method","path",
        "http_status","user_agent","host","raw","extra"
    }
    extra = ev.get("extra")
    if extra is None:
        extra = {k: v for k, v in ev.items() if k not in core_keys}
    extra_json = json.dumps(extra, ensure_ascii=False) if extra else None

    return (ts, source, event_type, ip, username, status, method, path, http_status, user_agent, host, raw, extra_json)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=os.getenv("DB_NAME", "socmini"))
    ap.add_argument("--file", required=True, help="JSONL file (normalized) to ingest")
    ap.add_argument("--source-type", default="mixed", help="web|auth|mixed (for ingest_runs)")
    ap.add_argument("--batch-size", type=int, default=1000)
    args = ap.parse_args()

    host = os.getenv("DB_HOST", "127.0.0.1")
    port = int(os.getenv("DB_PORT", "3306"))
    user = getenv_required("DB_USER")
    password = getenv_required("DB_PASS")

    cnx = mysql.connector.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=args.db,
        autocommit=False,
    )
    cur = cnx.cursor()

    # Create ingest run record
    cur.execute(
        "INSERT INTO ingest_runs (source_file, source_type) VALUES (%s,%s)",
        (args.file, args.source_type),
    )
    run_id = cur.lastrowid
    cnx.commit()

    inserted = 0
    batch = []

    try:
        for ev in read_jsonl(args.file):
            batch.append(event_to_row(ev))
            if len(batch) >= args.batch_size:
                cur.executemany(INSERT_SQL, batch)
                inserted += len(batch)
                cnx.commit()
                batch.clear()

        if batch:
            cur.executemany(INSERT_SQL, batch)
            inserted += len(batch)
            cnx.commit()

        cur.execute(
            "UPDATE ingest_runs SET finished_at=NOW(), events_inserted=%s WHERE id=%s",
            (inserted, run_id),
        )
        cnx.commit()

        print(f"[+] Ingested {inserted} events from {args.file} into {args.db}.events (run_id={run_id})")

    except Exception as e:
        cnx.rollback()
        cur.execute(
            "UPDATE ingest_runs SET finished_at=NOW(), notes=%s WHERE id=%s",
            (f"FAILED: {type(e).__name__}: {e}", run_id),
        )
        cnx.commit()
        raise
    finally:
        cur.close()
        cnx.close()


if __name__ == "__main__":
    main()
