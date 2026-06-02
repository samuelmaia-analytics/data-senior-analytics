# Security Policy

## Supported Versions
The `main` branch is the supported line for security fixes.

## Reporting a Vulnerability
Please do not open public issues for potential vulnerabilities.

Send details to:
- Email: `smaia2@gmail.com`
- Subject: `Security Report - data-analytics-workflow`

Include:
- Affected file/module
- Reproduction steps
- Potential impact
- Suggested remediation (optional)

## Security Controls in This Repository
- Secret pattern scan in CI (`scripts/check_secrets.py`).
- Environment variables externalized via `.env` and `.streamlit/secrets.toml`.
- Data provenance and contract checks for analytics outputs.
