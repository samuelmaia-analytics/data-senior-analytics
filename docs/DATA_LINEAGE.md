# Data Lineage and Reproducibility

## Purpose
Document how data artifacts are tracked so analytical outputs can be reproduced and reviewed with confidence.

## Manifest Strategy
- Manifest file: `docs/data_manifest.json`
- Generator: `scripts/generate_data_manifest.py`
- Scope: `data/sample/*` and `data/raw/*` tabular files
- Tracked fields per file:
  - relative path
  - file size in bytes
  - last modified timestamp in UTC
  - SHA-256 checksum
  - optional shape metadata (`rows`, `columns`) for CSV/XLSX

## Operational Flow
1. Add or update dataset files.
2. Regenerate the manifest:
   - `python scripts/generate_data_manifest.py`
3. Validate locally or in CI:
   - `python scripts/generate_data_manifest.py --check`

## Why This Matters
- Detects unintended data drift in versioned datasets.
- Increases confidence in reproducibility for reviewers and technical leads.
- Creates lightweight lineage documentation without introducing heavy platform dependencies.

## Portfolio Note
- The lineage process is a practical implementation for portfolio use.
- It is designed to demonstrate organization, traceability, and reproducibility fundamentals.
