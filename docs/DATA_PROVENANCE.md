# Data Provenance - Kaggle

## Status
- Official project source: **Kaggle**
- Raw data versioned in Git: **no**
- Mandatory source registration before release: **yes**
- Current provenance status: **approved**

## Source Record
- Dataset name: `Credit Risk Benchmark Dataset`
- Reference URL: `https://www.kaggle.com/datasets?datasetId=7083324`
- Kaggle Dataset ID: `7083324`
- Kaggle Source ID (`datasetVersion`): `11324518`
- Owner/publisher: `not_available_in_notebook_metadata`
- License: `not_available_in_notebook_metadata`
- Snapshot date identified in the notebook: `2025-05-01`
- Registration date in the project: `2026-03-03`
- Acquisition method: `kaggle_notebook_datasource`
- Evidence notebook: `data/raw/classifica-o-de-inadimpl-ncia.ipynb`

## Traceability Note
- This record was extracted from the internal Kaggle notebook metadata (`metadata.kaggle.dataSources`).
- When available, replace `owner` and `license` with the official values from the public dataset page.

## Governance Rules
- Always register the official Kaggle URL and the snapshot date used.
- Do not commit raw files under `data/raw/`.
- Synthetic example files are for local demonstration only.
- Any business-facing report must cite the dataset source and license.

## Reproducibility Evidence
- Source configuration: [config/data_source.yaml](../config/data_source.yaml)
- Provenance validation script: [scripts/validate_data_provenance.py](../scripts/validate_data_provenance.py)
- Synthetic data generator (optional): [scripts/generate_sample_data.py](../scripts/generate_sample_data.py)
