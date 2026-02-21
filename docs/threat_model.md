## Assets

- Authentication logs (usernames, timestamps, IPs)
- Web access logs (paths, user agents, IPs)
- Detection outputs (alerts/incidents)
- Database (events + detections)

## Adversaries (realistic)

- External attacker brute-forcing SSH
- Web scanner enumerating endpoints
- Credential stuffing patterns (many usernames from one IP)
- Insider or compromised host generating suspicious activity

## Attacks you will detect (project scope)

- Brute force SSH: many failed logins from same IP in time window
- Username spraying: many usernames from same IP
- Web scanning: many 404s + high request volume
- Suspicious user agent: common scanner UAs (optional)

## Trust boundaries

- Raw logs are untrusted input
- Parser must be resilient to malformed lines
- DB credentials must be protected via env vars

## Security assumptions (for a portfolio project)

- Logs may be incomplete or tampered → detection is “best effort”
- This is not a full SIEM; it’s a mini pipeline demo
