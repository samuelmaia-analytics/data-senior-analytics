# Data Contract

## Objective
Define expected schemas and quality rules across `raw`, `bronze`, `silver`, and `gold` layers so downstream dashboards and analyses are stable.

## Layer Contracts

### Raw
- Source: user-uploaded `.csv` or `.xlsx`.
- Required properties:
  - File is readable.
  - Header row exists.
  - At least 1 data row.
- No strict column naming enforcement.

### Bronze
- Purpose: preserve source fidelity after ingestion.
- Required properties:
  - Column names retained from source.
  - Row count equal to Raw input.
  - Metadata tracked (ingestion timestamp/source file).

### Silver
- Purpose: standardized dataset for analytics.
- Required properties:
  - Normalized snake_case column names.
  - Duplicates removed (business key or full row).
  - Missing values handled per strategy.
  - Best-effort dtype normalization (numeric/date/categorical).

### Gold
- Purpose: dashboard-ready business outputs.
- Minimum schema expected by contract tests:
  - `metric_name` (string, non-null)
  - `metric_value` (numeric, non-null)
  - `segment` (string, non-null)
  - `reference_date` (datetime-like, non-null)
- Quality rules:
  - `metric_name` + `segment` + `reference_date` must be unique.
  - `metric_value` must be finite.
  - Gold output must contain at least one row.

## Validation Strategy
- Unit tests validate schema and quality constraints for Gold outputs.
- CI blocks merges when output contract tests fail.
