#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

: "${DB_USER:?Set DB_USER}"
: "${DB_PASS:?Set DB_PASS}"
: "${DB_HOST:=127.0.0.1}"
: "${DB_PORT:=3306}"

mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASS" < db/schema.sql
echo "[+] Database schema applied."
