#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from datetime import datetime, timezone
from typing import Optional, Tuple

from parser.normalize import Event, write_jsonl, ensure_iso8601

# Example:
# 1.2.3.4 - - [22/Feb/2026:16:03:12 +0000] "GET /login HTTP/1.1" 404 123 "-" "curl/8.1.2"
WEB_RE = re.compile(
    r'^(?P<ip>\S+)\s+\S+\s+\S+\s+\[(?P<ts>[^\]]+)\]\s+'
    r'"(?P<method>[A-Z]+)\s+(?P<path>\S+)\s+HTTP/(?P<httpver>\d\.\d)"\s+'
    r'(?P<status>\d{3})\s+(?P<size>\d+)\s+"(?P<ref>[^"]*)"\s+"(?P<ua>[^"]*)"\s*$'
)

def parse_apache_ts(ts: str) -> Optional[datetime]:
    # "22/Feb/2026:16:03:12 +0000"
    try:
        dt = datetime.strptime(ts, "%d/%b/%Y:%H:%M:%S %z")
        return dt.astimezone(timezone.utc)
    except Exception:
        return None

def classify_http(path: str, http_status: int, method: str) -> str:
    
    if path in ("/login", "/signin", "/admin/login") and method == "POST" and http_status in (401, 403):
        return "web_login_failed"
    if http_status == 404:
        return "web_404"
    if http_status == 403:
        return "web_forbidden"
    return "http_request"

def parse_line(line: str) -> Optional[Event]:
    m = WEB_RE.match(line.strip())
    if not m:
        return None

    ip = m.group("ip")
    ts_raw = m.group("ts")
    dt = parse_apache_ts(ts_raw)
    ts = ensure_iso8601(dt) if dt else ensure_iso8601(ts_raw)

    method = m.group("method")
    path = m.group("path")
    http_status = int(m.group("status"))
    ua = m.group("ua")

    event_type = classify_http(path, http_status, method)

    status = "success" if 200 <= http_status < 400 else "fail"

    return Event(
        timestamp=ts,
        source="web",
        event_type=event_type,
        ip=ip,
        status=status,
        method=method,
        path=path,
        http_status=http_status,
        user_agent=ua,
        raw=line.strip(),
    )

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--in", dest="inp", default="data/raw/web_access.log")
    p.add_argument("--out", dest="outp", default="data/normalized/web_events.jsonl")
    args = p.parse_args()

    events: list[Event] = []
    total = 0
    bad = 0

    with open(args.inp, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            total += 1
            ev = parse_line(line)
            if ev is None:
                bad += 1
                continue
            events.append(ev)

    write_jsonl(args.outp, events)
    print(f"[+] Parsed web logs: {len(events)}/{total} lines -> {args.outp}")
    if bad:
        print(f"[i] Skipped {bad} unparsable lines")

if __name__ == "__main__":
    main()
