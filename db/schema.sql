-- soc-mini-platform/db/schema.sql
CREATE DATABASE IF NOT EXISTS socmini
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;

USE socmini;

-- Track ingestions (optional but nice for debugging)
CREATE TABLE IF NOT EXISTS ingest_runs (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  finished_at TIMESTAMP NULL,
  source_file VARCHAR(255) NOT NULL,
  source_type VARCHAR(32) NOT NULL, -- 'web' or 'auth' or 'mixed'
  events_inserted INT NOT NULL DEFAULT 0,
  notes VARCHAR(255) NULL
) ENGINE=InnoDB;

-- Main events table
CREATE TABLE IF NOT EXISTS events (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,

  ts DATETIME(6) NOT NULL,          -- normalized timestamp (UTC)
  source VARCHAR(16) NOT NULL,      -- web/auth
  event_type VARCHAR(64) NOT NULL,  -- ssh_failed, http_request, web_404, etc.

  ip VARCHAR(45) NULL,              -- supports IPv4/IPv6
  username VARCHAR(128) NULL,

  status VARCHAR(16) NULL,          -- success/fail
  method VARCHAR(16) NULL,
  path VARCHAR(2048) NULL,
  http_status SMALLINT NULL,
  user_agent VARCHAR(512) NULL,
  host VARCHAR(255) NULL,

  raw TEXT NULL,                    -- original log line (optional)
  extra JSON NULL,                  -- room for future enrichment

  -- useful indexes for SOC queries
  INDEX idx_ts (ts),
  INDEX idx_source_type (source, event_type),
  INDEX idx_ip_ts (ip, ts),
  INDEX idx_user_ts (username, ts),
  INDEX idx_http_status (http_status)
) ENGINE=InnoDB;

-- new detections table 
CREATE TABLE IF NOT EXISTS detections (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  detected_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

  rule_name VARCHAR(128) NOT NULL,
  severity VARCHAR(32) NOT NULL,

  ip VARCHAR(45) NULL,
  username VARCHAR(128) NULL,

  event_count INT NOT NULL,
  first_seen DATETIME(6) NULL,
  last_seen DATETIME(6) NULL,

  details JSON NULL,

  INDEX idx_rule (rule_name),
  INDEX idx_ip (ip),
  INDEX idx_detected_at (detected_at)
) ENGINE=InnoDB;
