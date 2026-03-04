# ADR-0003: Kaggle Dataset Provenance as Mandatory Gate

## Status
Accepted

## Context
Executive credibility requires traceable real-world data sources.

## Decision
Enforce dataset provenance metadata in `config/data_source.yaml` and validate in CI.

## Consequences
- Positive: stronger auditability, reproducibility, and trust in results.
- Negative: adds metadata maintenance overhead when dataset changes.
