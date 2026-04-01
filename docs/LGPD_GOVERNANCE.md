# LGPD Governance

## Scope
This project now applies basic privacy governance controls for analytics workflows that may receive personal data through uploads.

## What Is Enforced in the Product
- Detection of likely personal, quasi-identifying, and sensitive columns based on column names and content patterns.
- Masked previews in the dashboard when personal data is detected.
- LGPD risk classification in the product surface (`Minimal`, `Low`, `Medium`, `High`).
- Extra acknowledgement before persisting personal data into SQLite.
- Masked persistence enabled by default when personal data is detected.
- Persistence registry with retention metadata and audit log in SQLite.

## Why These Controls Exist
The LGPD defines:
- `dados pessoais` and `dados pessoais sensíveis` in Article 5.
- principles such as purpose limitation, adequacy, and necessity in Article 6.

These controls are aligned with those ideas:
- minimize exposure in the interface
- reduce unnecessary persistence of direct identifiers
- make privacy risk explicit before analytical reuse

## Important Limitation
This repository does **not** claim legal compliance by itself.
It provides engineering controls that support a privacy-by-design posture, but lawful basis, retention, access control, incident handling, and formal governance still depend on the operating context.

## Engineering Interpretation
- Dashboard previews are treated as a lower-trust surface and should not expose direct identifiers by default.
- SQLite persistence is treated as a control point, not a neutral storage action.
- Governance metadata should accompany analytical quality metadata.
- Retention must be explicit at persistence time, not inferred after the fact.

## References
- Brazil LGPD official text: Lei nº 13.709/2018, especially Articles 5 and 6.
- ANPD guidance on anonymization and privacy governance.
