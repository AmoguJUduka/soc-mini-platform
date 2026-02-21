#!/usr/bin/env bash
set -euo pipefail

RAW_DIR="data/raw"
mkdir -p "$RAW_DIR"

# 1) Collect auth logs (best effort, varies by distro)
# RHEL/CentOS: /var/log/secure
# Debian/Ubuntu: /var/log/auth.log
AUTH_SRC=""
if [[ -f /var/log/secure ]]; then
  AUTH_SRC="/var/log/secure"
elif [[ -f /var/log/auth.log ]]; then
  AUTH_SRC="/var/log/auth.log"
fi

if [[ -n "$AUTH_SRC" ]]; then
  cp "$AUTH_SRC" "$RAW_DIR/auth.log"
  echo "[+] Copied auth log from $AUTH_SRC -> $RAW_DIR/auth.log"
else
  echo "[!] No auth log found at /var/log/secure or /var/log/auth.log"
  echo "    (This is OK for now — you can add a sample later.)"
fi

# 2) Generate web logs into raw folder
python3 simulator/web_log_generator.py -o "$RAW_DIR/web_access.log" --minutes 15 --rate 40 --attack-burst

echo "[+] Raw logs ready in $RAW_DIR/"
ls -lh "$RAW_DIR"
