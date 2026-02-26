# SOC Mini-Platform (Mini SIEM)

A small SOC-style pipeline that ingests logs, normalizes events, runs detection rules (e.g., brute force / scanning), stores results in MySQL, and generates incident reports.

## Project Goals
- Collect raw logs (Linux auth + generated web access logs)
- Normalize into a common event schema (Python)
- Store events + detections in MySQL
- Run detection rules with time windows
- Produce reproducible incident reports

## Architecture
See: `docs/architecture.md`

## Detection Use Cases (Planned)
- SSH brute force (high failed-login rate per IP)
- Username spraying (many usernames from one IP)
- Web scanning (many 404s + endpoint enumeration)
- Suspicious user-agent detection (optional)

## Repo Structure
- `collector/` - log collection scripts
- `simulator/` - attack + traffic generators
- `parser/` - parsing + normalization modules
- `db/` - MySQL schema and ingestion code
- `detections/` - detection rules engine
- `reports/` - incident report generator
- `data/` - raw and normalized datasets (gitignored)

## Disclaimer
This project is for defensive security learning and detection engineering practice.
