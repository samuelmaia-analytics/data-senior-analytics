# Streamlit Cloud Deployment

## Deployment Contract
- Entrypoint: `dashboard/app.py`
- Runtime: `python-3.11` in [runtime.txt](../runtime.txt)
- Dependency source: [requirements.txt](../requirements.txt)
- Streamlit version: `1.54.0`

## Repository Readiness
- Keep `.streamlit/config.toml` at repo root.
- Keep `.streamlit/secrets.toml` out of git; use `.streamlit/secrets.example.toml` as template.
- Ensure demo data remains available in `data/sample/` for smoke tests.

## Important Operational Lessons
- If the app was originally created with the wrong Python version, redeploy alone may not be enough.
- If Streamlit Cloud keeps using the wrong Python runtime, delete the app and recreate it with `Python 3.11`.
- Prefer a single dependency source for the app. This repository keeps runtime dependencies only in `requirements.txt`; tooling config lives in dedicated files such as `pytest.ini`, `ruff.toml`, `.coveragerc`, and `mypy.ini`.

## App Creation Settings
- Repository: `samuelmaia-analytics/data-senior-analytics`
- Branch: `main`
- Main file path: `dashboard/app.py`
- Python version: `3.11`

## Local Pre-Deploy Checks
```bash
python -m ruff check src config scripts dashboard tests
python -m black --check src config scripts dashboard tests
python -m pytest
python scripts/check_encoding.py
python scripts/streamlit_cloud_preflight.py
python scripts/validate_data_provenance.py
python scripts/generate_data_manifest.py --check
```

## Smoke Test Checklist
1. Open the deployed URL.
2. Confirm the `Overview` page renders without tracebacks.
3. Navigate through `Upload`, `Data`, `EDA`, `Visualizations`, `Database`, and `Settings`.
4. Upload a CSV/XLSX and verify the quality score updates.
5. Save the curated dataset into SQLite and verify it appears in `Database`.

## Troubleshooting
- `Python 3.14.x` in logs:
  Recreate the app and pin `Python 3.11`.
- Dependency installs but app crashes on widget arguments:
  Check Streamlit version compatibility between code and `requirements.txt`.
- Dependency resolution takes the wrong file:
  Confirm `requirements.txt` contains the runtime dependencies and keep the repo root clean.
