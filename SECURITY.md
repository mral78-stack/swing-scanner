# Security Policy

## Reporting a vulnerability

If you find a security issue, please **do not** open a public issue. Instead, email the maintainer at the address listed on the GitHub profile, or open a [private security advisory](https://github.com/mral78-stack/swing-scanner/security/advisories/new).

You can expect an initial response within 7 days.

## Scope

This project is a read-only market data scanner. It does not place trades, hold credentials beyond optional read-only data-provider API keys, and does not persist user data outside of local cache files under `scanner_cache/`.

Realistic risk areas:

- **Dependency vulnerabilities** — `yfinance`, `requests`, `streamlit`, `pandas`. Reports for upstream CVEs that are not actually triggered by this code are welcome but lower priority.
- **API key exposure** — keys are read from environment variables. If you find a code path that logs or persists them, that's a real bug.
- **Streamlit dashboard XSS / SSRF** — anything where unsanitized user input flows to a render or outbound request.

## Out of scope

- "The scanner gave a bad signal." That's a modelling concern, not a security issue.
- Issues that require the attacker to already control the machine running the scanner.

## Disclosure timeline

- Acknowledge within 7 days
- Triage within 14 days
- Fix or public advisory within 90 days
