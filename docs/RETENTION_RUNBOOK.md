# Retention Runbook

## Objective
Define how retained datasets are tracked, reviewed, and removed from SQLite.

## Current Behavior
- Every persisted dataset receives:
  - `retention_days`
  - `retention_until`
  - `persistence_mode`
  - privacy flags
- The app checks for expired datasets on `Overview` load.
- Expired datasets are dropped automatically.
- Every purge is written to the SQLite audit log.

## Operating Steps
1. Review `Database` > `Persistence Registry`.
2. Check `Expiring in 14d` on the `Overview`.
3. Confirm whether datasets nearing expiry must be re-persisted or allowed to expire.
4. Review `Audit Log` for purge and persistence history.

## Persistence Modes
- `curated`: curated dataset stored without masking
- `masked`: masked dataset stored to reduce direct identifier exposure

## Recommended Practice
- Use `masked` mode by default when personal data is detected.
- Only persist unmasked data when lawful basis and operational need are both clear.
- Keep retention short for uploaded datasets that contain personal or sensitive data.

## Limitation
The current purge is triggered by app execution. A production-grade setup should also run the same policy through a scheduled job.
