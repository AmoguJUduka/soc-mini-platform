#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

: "${DB_USER:?Set DB_USER}"
: "${DB_PASS:?Set DB_PASS}"
: "${DB_HOST:=127.0.0.1}"
: "${DB_PORT:=3306}"
: "${DB_NAME:=socmini}"

python3 db/ingest.py --db "$DB_NAME" --file data/normalized/web_events.jsonl --source-type web
python3 db/ingest.py --db "$DB_NAME" --file data/normalized/auth_events.jsonl --source-type auth || true
