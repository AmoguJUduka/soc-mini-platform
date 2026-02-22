#!/usr/bin/env python3
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, Optional


def iso_utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_iso8601(ts: Any) -> str:
    """
    Return ISO-8601 string in UTC if possible.
    Accepts datetime or string; if string already, return as-is.
    """
    if isinstance(ts, datetime):
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        return ts.astimezone(timezone.utc).isoformat()
    if isinstance(ts, str):
        return ts
    return iso_utc_now()


@dataclass
class Event:
    timestamp: str
    source: str                 # "web" | "auth"
    event_type: str             # "http_request" | "ssh_failed" | ...
    ip: Optional[str] = None
    username: Optional[str] = None
    status: Optional[str] = None
    method: Optional[str] = None
    path: Optional[str] = None
    http_status: Optional[int] = None
    user_agent: Optional[str] = None
    host: Optional[str] = None
    raw: Optional[str] = None
    extra: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        # drop None fields for cleaner storage
        return {k: v for k, v in d.items() if v is not None}


def write_jsonl(path: str, events: list[Event]) -> None:
    import os
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for ev in events:
            f.write(json.dumps(ev.to_dict(), ensure_ascii=False) + "\n")
