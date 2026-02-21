#!/usr/bin/env python3
"""
Generate realistic-looking web access logs with a mix of benign traffic and
attack-like patterns (scanning, brute force-style login attempts).

Output format: Common/Combined-ish log:
<ip> - - [date] "METHOD PATH HTTP/1.1" STATUS BYTES "REF" "UA"
"""

from __future__ import annotations

import argparse
import random
import time
from datetime import datetime, timedelta, timezone



"""
UAS_BENIGN: A collection of "Regular Joe" User Agent strings.
These represent legitimate browsers (Chrome, Safari, Firefox) across 
different operating systems (Windows, macOS, Linux, iOS, Android). 
Used in the simulation to create a baseline of normal human traffic 
to mask or contrast against automated scanning tools.
"""

UAS_BENIGN = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) AppleWebKit/605.1.15 Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) Gecko/20100101 Firefox/121.0",
]
"""
UAS_SCANNERS: A list of non-browser identities.
These represent automated tools (curl, wget) and security scanners (Nikto, Nmap).
In a real log, these are "low-hanging fruit" for security teams to flag 
because legitimate human users almost never use these strings to browse a site.
"""
UAS_SCANNERS = [
    "curl/8.1.2",
    "Wget/1.21.3",
    "python-requests/2.31.0",
    "Mozilla/5.0 zgrab/0.x",
    "masscan/1.3",
    "Nmap Scripting Engine",
    "Nikto/2.1.6",
]


"""
BENIGN_PATHS: A collection of public-facing, "safe" URLs.
These represent the standard content a normal visitor would access.
In log analysis, these typically correlate with '200 OK' status codes 
and come from legitimate browser User Agents.
"""

BENIGN_PATHS = [
    "/", "/index.html", "/about", "/pricing", "/docs", "/contact",
    "/assets/app.css", "/assets/app.js", "/favicon.ico",
]

"""
SCAN_PATHS: A "hit list" of sensitive or hidden directories.
These include configuration files (.env), admin logins (/wp-admin),
and known exploit paths. In a security context, any request to 
these paths is considered suspicious and usually results in a 403 or 404.
"""


SCAN_PATHS = [
    "/admin", "/wp-admin", "/phpmyadmin", "/.env", "/config.php", "/server-status",
    "/api", "/api/v1/users", "/login", "/robots.txt", "/sitemap.xml",
    "/.git/config", "/vendor/phpunit/phpunit/src/Util/PHP/eval-stdin.php",
]


"""
LOGIN_PATHS: Targeted endpoints for authentication.
In the attack simulation, these are paired with POST methods and 401/403 
status codes to mimic "credential spraying"—where an attacker tries 
common passwords against an account.
"""
LOGIN_PATHS = ["/login", "/signin", "/admin/login"]
METHODS = ["GET", "POST"]

def apache_time(dt: datetime) -> str:
    # Format: 10/Oct/2000:13:55:36 +0000
    return dt.strftime("%d/%b/%Y:%H:%M:%S %z")

def rand_ip(private_bias: bool = True) -> str:
    # A mix of public-ish and RFC1918
    if private_bias and random.random() < 0.35:
        return f"192.168.{random.randint(0,255)}.{random.randint(1,254)}"
    return f"{random.randint(11,223)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"

def emit_line(ts: datetime, ip: str, method: str, path: str, status: int, size: int, ref: str, ua: str) -> str:
    return f'{ip} - - [{apache_time(ts)}] "{method} {path} HTTP/1.1" {status} {size} "{ref}" "{ua}"'

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("-o", "--out", default="data/raw/web_access.log", help="Output file path")
    p.add_argument("--minutes", type=int, default=10, help="Timespan in minutes")
    p.add_argument("--rate", type=int, default=30, help="Approx requests per minute")
    p.add_argument("--seed", type=int, default=None, help="Random seed")
    p.add_argument("--attack-burst", action="store_true", help="Include an obvious scanning burst")
    args = p.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    now = datetime.now(timezone.utc)
    start = now - timedelta(minutes=args.minutes)

    # Define a couple of "bad actors" for repeatable signals
    scanner_ip = rand_ip(private_bias=False)
    spray_ip = rand_ip(private_bias=False)

    total = args.minutes * args.rate
    lines: list[str] = []

    for i in range(total):
        # Spread timestamps roughly across the timespan
        ts = start + (now - start) * (i / max(total - 1, 1))

        r = random.random()
        if r < 0.78:
            # Benign browsing
            ip = rand_ip()
            path = random.choice(BENIGN_PATHS)
            method = "GET"
            status = 200 if not path.endswith(".ico") else 200
            size = random.randint(200, 5000)
            ref = "https://example.com/" if random.random() < 0.6 else "-"
            ua = random.choice(UAS_BENIGN)

        elif r < 0.93:
            # Light probing / occasional 404s
            ip = rand_ip(private_bias=False)
            path = random.choice(SCAN_PATHS + BENIGN_PATHS)
            method = random.choice(METHODS)
            # More likely 404 on scan paths
            status = 404 if path in SCAN_PATHS and random.random() < 0.75 else random.choice([200, 301, 403])
            size = random.randint(100, 4000)
            ref = "-"
            ua = random.choice(UAS_BENIGN + ["curl/8.1.2"])

        else:
            # Attack-like traffic: scanning + login attempts
            if random.random() < 0.6:
                ip = scanner_ip
                path = random.choice(SCAN_PATHS)
                method = "GET"
                status = random.choice([404, 403, 404, 404])
                ua = random.choice(UAS_SCANNERS)
                size = random.randint(50, 1500)
                ref = "-"
            else:
                ip = spray_ip
                path = random.choice(LOGIN_PATHS)
                method = "POST"
                status = random.choice([401, 401, 401, 403])
                ua = random.choice(UAS_SCANNERS + ["python-requests/2.31.0"])
                size = random.randint(200, 1200)
                ref = "-"

        lines.append(emit_line(ts, ip, method, path, status, size, ref, ua))

    # Optional: a very obvious burst (good for demo)
    if args.attack_burst:
        burst_start = now - timedelta(minutes=2)
        for j in range(160):
            ts = burst_start + timedelta(seconds=j)
            path = random.choice(SCAN_PATHS)
            lines.append(emit_line(ts, scanner_ip, "GET", path, 404, random.randint(40, 800), "-", random.choice(UAS_SCANNERS)))

    out_path = args.out
    # Ensure parent dirs exist
    import os
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"[+] Wrote {len(lines)} web log lines to {out_path}")
    print(f"[i] Scanner IP: {scanner_ip}")
    print(f"[i] Spray IP:   {spray_ip}")

if __name__ == "__main__":
    main()
