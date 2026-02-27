#!/usr/bin/env python3
from __future__ import annotations
import os
import mysql.connector
from datetime import datetime

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        database=os.getenv("DB_NAME", "socmini"),
    )

def insert_detection(cur, rule_name, severity, ip, username, count, first_seen, last_seen, details):
    cur.execute("""
        INSERT INTO detections
        (rule_name, severity, ip, username, event_count, first_seen, last_seen, details)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """, (rule_name, severity, ip, username, count, first_seen, last_seen, details))

def detect_ssh_bruteforce(cur):
    cur.execute("""
        SELECT ip, COUNT(*), MIN(ts), MAX(ts)
        FROM events
        WHERE event_type='ssh_failed'
        GROUP BY ip
        HAVING COUNT(*) >= 5
    """)
    for ip, count, first_seen, last_seen in cur.fetchall():
        insert_detection(cur,
            "SSH Brute Force",
            "HIGH",
            ip,
            None,
            count,
            first_seen,
            last_seen,
            '{"description": "Multiple SSH failures detected"}'
        )

def detect_username_spray(cur):
    cur.execute("""
        SELECT ip, COUNT(DISTINCT username), MIN(ts), MAX(ts)
        FROM events
        WHERE event_type='ssh_failed'
        GROUP BY ip
        HAVING COUNT(DISTINCT username) >= 3
    """)
    for ip, count, first_seen, last_seen in cur.fetchall():
        insert_detection(cur,
            "Username Spraying",
            "HIGH",
            ip,
            None,
            count,
            first_seen,
            last_seen,
            '{"description": "Multiple usernames targeted from single IP"}'
        )

def detect_web_scanning(cur):
    cur.execute("""
        SELECT ip, COUNT(*), MIN(ts), MAX(ts)
        FROM events
        WHERE event_type='web_404'
        GROUP BY ip
        HAVING COUNT(*) >= 20
    """)
    for ip, count, first_seen, last_seen in cur.fetchall():
        insert_detection(cur,
            "Web Scanning Activity",
            "MEDIUM",
            ip,
            None,
            count,
            first_seen,
            last_seen,
            '{"description": "High 404 rate detected"}'
        )

def main():
    conn = get_connection()
    cur = conn.cursor()

    detect_ssh_bruteforce(cur)
    detect_username_spray(cur)
    detect_web_scanning(cur)

    conn.commit()
    cur.close()
    conn.close()

    print("[+] Detection run complete.")

if __name__ == "__main__":
    main()
