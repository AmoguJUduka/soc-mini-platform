#!/usr/bin/env bash
set -euo pipefail

echo "[*] Day 2 demo: generate and collect raw logs"
cd "$(dirname "$0")/.."

bash collector/collect_logs.sh
echo "[+] Done. Next: Day 3 will parse/normalize these logs."
