# Streamlit Cloud Deployment (Executive Standard)

## 1. Repository Readiness
- Main entrypoint: `dashboard/app.py`
- Runtime pin: `runtime.txt`
- Production dependencies: `requirements.txt`
- Secrets template: `.streamlit/secrets.example.toml`
- Data provenance: `docs/DATA_PROVENANCE.md` and `config/data_source.yaml`

## 2. Streamlit Cloud App Settings
- Repository: `samuelmaia-analytics/data-senior-analytics`
- Branch: `main`
- Main file path: `dashboard/app.py`
- Python version: read from `runtime.txt`

## 3. Secrets and Configuration
- Open Streamlit Cloud app settings -> `Secrets`
- Paste values based on `.streamlit/secrets.example.toml`
- Never commit `.streamlit/secrets.toml`

## 4. Data Governance Requirements
- Use real Kaggle dataset only
- Register exact dataset metadata in `config/data_source.yaml` and set `provenance_status=approved`
- Keep raw files out of Git (`data/raw/*` ignored)

Optional helper:

```bash
python scripts/set_kaggle_provenance.py \
  --dataset-name "YOUR_DATASET_NAME" \
  --dataset-url "https://www.kaggle.com/datasets/USER/DATASET" \
  --owner "USER" \
  --license "LICENSE_NAME"
```

## 5. Pre-Deploy Quality Gates
Optional shortcut:

```bash
make quality
```

Run locally before publish:

```bash
python -m ruff check src config scripts dashboard tests
python -m pytest
python scripts/check_encoding.py
python scripts/streamlit_cloud_preflight.py
python scripts/validate_data_provenance.py
```

## 6. Post-Deploy Smoke Test
- Open deployed URL
- Validate upload page
- Validate one end-to-end flow:
  - upload CSV/XLSX
  - run EDA view
  - render charts
  - save/read SQLite table
- Confirm no corrupted characters in UI text
