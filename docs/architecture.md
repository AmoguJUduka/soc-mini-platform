## Components

- Collector: grabs raw logs or generated logs → data/raw/
- Parser/Normalizer (Python): transforms into common event schema → data/normalized/
- DB Ingest (Python): inserts into MySQL tables
- Detections Engine (Python): runs rules, stores alerts
- Reports (Python): generates Markdown incident report
