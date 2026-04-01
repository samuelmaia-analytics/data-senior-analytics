# Streamlit Cloud Deployment

## Deployment Contract
- Entrypoint: `dashboard/app.py`
- Runtime: `python-3.11` in [runtime.txt](../runtime.txt)
- Runtime dependencies: [requirements.txt](../requirements.txt)
- Streamlit version: `1.54.0`

## Operational Principles
- Keep exactly one runtime dependency source for the deployed app.
- Treat Python version as a deployment contract, not as a best-effort preference.
- Validate the dashboard as a product surface after each deploy, not only dependency installation.

## Repository Readiness
- Keep `.streamlit/config.toml` at the repository root.
- Keep `.streamlit/secrets.toml` out of git; use `.streamlit/secrets.example.toml` as the template.
- Keep demo datasets under `data/sample/` available for smoke tests and fallbacks.

## App Creation Settings
- Repository: `samuelmaia-analytics/data-senior-analytics`
- Branch: `main`
- Main file path: `dashboard/app.py`
- Python version: `3.11`

## Local Pre-Deploy Checks
```bash
python -m ruff check src config scripts dashboard tests
python -m black --line-length 100 --target-version py311 --check src config scripts dashboard tests
python -m pytest
python scripts/check_encoding.py
python scripts/streamlit_cloud_preflight.py
python scripts/validate_data_provenance.py
python scripts/generate_data_manifest.py --check
```

## Smoke Test Checklist
1. Open the deployed URL.
2. Confirm `Overview` renders without tracebacks.
3. Confirm `Overview` shows decision risk, confidence, and release posture.
4. Navigate through `Upload`, `Data`, `EDA`, `Visualizations`, `Database`, and `Settings`.
5. Upload a CSV/XLSX and confirm the quality score updates.
6. Save the curated dataset into SQLite and confirm it appears in `Database`.

## Troubleshooting
- App still starts with `Python 3.14.x`:
  Delete the app and recreate it with `Python 3.11`.
- Dependencies install but the app crashes on startup:
  Check Streamlit API compatibility between the deployed version and the codebase.
- Streamlit Cloud warns about multiple dependency sources:
  The repository should expose runtime dependencies only through `requirements.txt`.
