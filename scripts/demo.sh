#!/usr/bin/env bash
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

echo "[*] Demo: collect raw logs"
bash collector/collect_logs.sh

echo "[*] Demo: parse + normalize"
bash scripts/parse.sh

echo "[+] Done."
