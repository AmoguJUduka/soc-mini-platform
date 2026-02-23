#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from datetime import datetime, timezone
from typing import Optional

from parser.normalize import Event, write_jsonl, ensure_iso8601

# Handles both Debian (/var/log/auth.log) and RHEL (/var/log/secure) style prefixes
# Examples:
# Feb 22 12:34:56 server1 sshd[1234]: Failed password for invalid user admin from 1.2.3.4 port 5555 ssh2
# Feb 22 12:34:56 server1 sshd[1234]: Failed password for student from 1.2.3.4 port 5555 ssh2
# Feb 22 12:35:01 server1 sshd[1234]: Accepted password for student from 1.2.3.4 port 5555 ssh2

FAILED_RE = re.compile(
    r".*sshd\[\d+\]:\s+Failed password for (?:(invalid user)\s+)?(?P<user>\S+)\s+from\s+(?P<ip>\S+)"
)
ACCEPTED_RE = re.compile(
    r".*sshd\[\d+\]:\s+Accepted \S+ for (?P<user>\S+)\s+from\s+(?P<ip>\S+)"
)

PREFIX_RE = re.compile(r"^(?P<mon>\w{3})\s+(?P<day>\d{1,2})\s+(?P<time>\d{2}:\d{2}:\d{2})\s+(?P<host>\S+)\s+(?P<rest>.*)$")

MONTHS = {"Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,"Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12}

def parse_syslog_prefix(line: str) -> tuple[Optional[datetime], Optional[str], str]:
    """
    Parse 'Feb 22 12:34:56 host ...' into datetime (UTC-ish) and hostname.
    Syslog lines often omit year/timezone; we assume current year and localtime, then convert to UTC.
    For portfolio use, it's fine; later we can improve.
    """
    m = PREFIX_RE.match(line)
    if not m:
        return None, None, line.strip()

    mon = MONTHS.get(m.group("mon"))
    day = int(m.group("day"))
    t = m.group("time")
    host = m.group("host")
    rest = m.group("rest")

    if mon is None:
        return None, host, rest

    now = datetime.now().astimezone()
    year = now.year
    try:
        dt_local = datetime.strptime(f"{year}-{mon:02d}-{day:02d} {t}", "%Y-%m-%d %H:%M:%S")
        # assume local timezone
        dt_local = dt_local.replace(tzinfo=now.tzinfo)
        return dt_local.astimezone(timezone.utc), host, rest
    except Exception:
        return None, host, rest

def parse_line(line: str) -> Optional[Event]:
    dt, host, rest = parse_syslog_prefix(line)
    ts = ensure_iso8601(dt) if dt else ensure_iso8601(datetime.now(timezone.utc))

    m_fail = FAILED_RE.match(line)
    if m_fail:
        return Event(
            timestamp=ts,
            source="auth",
            event_type="ssh_failed",
            ip=m_fail.group("ip"),
            username=m_fail.group("user"),
            status="fail",
            host=host,
            raw=line.strip(),
        )

    m_ok = ACCEPTED_RE.match(line)
    if m_ok:
        return Event(
            timestamp=ts,
            source="auth",
            event_type="ssh_accepted",
            ip=m_ok.group("ip"),
            username=m_ok.group("user"),
            status="success",
            host=host,
            raw=line.strip(),
        )

    return None

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--in", dest="inp", default="data/raw/auth.log")
    p.add_argument("--out", dest="outp", default="data/normalized/auth_events.jsonl")
    args = p.parse_args()

    events: list[Event] = []
    total = 0
    bad = 0

    try:
        with open(args.inp, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                total += 1
                ev = parse_line(line)
                if ev is None:
                    bad += 1
                    continue
                events.append(ev)
    except FileNotFoundError:
        print(f"[!] No auth log found at {args.inp}. This is OK for Day 3.")
        print("    Run Day 2 collector again or add a sample auth.log to data/raw/")
        return

    write_jsonl(args.outp, events)
    print(f"[+] Parsed auth logs: {len(events)}/{total} lines -> {args.outp}")
    if bad:
        print(f"[i] Skipped {bad} non-ssh or unparsable lines")

if __name__ == "__main__":
    main()
