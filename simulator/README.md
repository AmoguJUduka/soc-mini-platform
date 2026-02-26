# Web Log Generator (Simulator)

The Web Log Generator simulates realistic **web access logs** for use in the SOC Mini-Platform (Mini SIEM).  
It is designed to create repeatable, high-signal log data that can be ingested, normalized, and analyzed
by detection rules.

This component enables security testing and detection development **without requiring live traffic**.

---

## Purpose

This simulator provides:
- Consistent and repeatable web access logs
- A mix of benign, suspicious, and malicious-looking activity
- Clear attack patterns suitable for detection demos and validation

It is primarily used to feed the SOC pipeline with web telemetry for:
- Brute-force detection
- Scanning detection
- Behavioral analysis over time windows

---

## What Kind of Logs Are Generated

The output resembles standard **Apache-style web access logs**, including:
- Source IP addresses
- Timestamps
- HTTP methods and requested paths
- HTTP status codes
- Response sizes
- Referrers
- User-Agent strings

Each log entry represents a single HTTP request event.

---

## Traffic Types Simulated

### 1) Normal User Traffic
Represents legitimate website visitors:
- Common browsers (Chrome, Firefox, Safari)
- Typical page requests (home, docs, static assets)
- Mostly successful responses (`200 OK`)

This traffic forms the baseline and majority of the dataset.

---

### 2) Suspicious / Background Noise
Represents low-level probing:
- Requests to uncommon or invalid paths
- Occasional failed responses (`404 Not Found`)
- Mixed request methods

This mimics real-world internet noise seen by public-facing servers.

---

### 3) Attack-Like Activity
Designed to trigger SOC detections:
- Repeated access to sensitive paths (configuration files, admin pages)
- High-frequency requests from a small number of IPs
- Repeated authentication attempts against login endpoints
- Unusual or automated user-agent strings

These behaviors simulate:
- Web scanning
- Credential spraying
- Brute-force login attempts

---

## Detection Value

The generated logs are intentionally structured to support:
- Rate-based detections (events per IP over time)
- Authentication failure analysis
- Path-based anomaly detection
- Correlation with other log sources (e.g., SSH auth logs)

Known “bad” IPs are injected to make validation and testing easier.

---

## Usage in the SOC Mini-Platform

Within the SOC Mini-Platform pipeline, the generated web logs are:

1. **Written to disk** as raw log files
2. **Ingested** by the pipeline
3. **Normalized** into a common event schema
4. **Stored** in MySQL
5. **Evaluated** by detection rules
6. **Referenced** in incident reports

This allows end-to-end SOC workflow testing using synthetic data.

---

## Why This Exists

Real production logs:
- Are difficult to share
- Contain sensitive data
- Are inconsistent across environments

This simulator solves those problems by providing:
- Safe, reproducible datasets
- Predictable attack signals
- A controlled environment for learning and experimentation

---

## Intended Extensions

Planned or possible future enhancements include:
- Additional attack patterns (SQL injection, path traversal)
- Session-based browsing behavior
- Error spikes and service degradation scenarios
- API endpoint simulation

---

## Summary

The Web Log Generator is a **foundational telemetry source** for the SOC Mini-Platform.
It enables realistic detection engineering, SOC workflow testing, and security education
without relying on live or sensitive production traffic.