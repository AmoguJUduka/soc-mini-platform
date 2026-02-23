#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

echo "[*] Parsing web logs..."
python3 -m parser.parse_web --in data/raw/web_access.log --out data/normalized/web_events.jsonl

echo "[*] Parsing auth logs..."
python3 -m parser.parse_auth --in data/raw/auth.log --out data/normalized/auth_events.jsonl || true

echo "[+] Normalized outputs:"
ls -lh data/normalized || true
