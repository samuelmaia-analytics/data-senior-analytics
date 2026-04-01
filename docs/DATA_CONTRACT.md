# Data Contract

## Objective
Define the minimum guarantees expected across `raw`, `bronze`, `silver`, and `gold` layers so downstream analysis, persistence, and decision reporting remain stable.

## Layer Guarantees

### Raw
- Source: user-uploaded `.csv` or `.xlsx`.
- Expectations:
  - File is readable.
  - Header row exists.
  - At least one data row exists.
- Rule:
  - No strict naming normalization at this stage.

### Bronze
- Purpose: preserve source fidelity immediately after ingestion.
- Expectations:
  - Original column names are still recognizable.
  - Row count matches the raw input.
  - Ingestion metadata is traceable.

### Silver
- Purpose: provide a standardized dataset ready for analytical use.
- Expectations:
  - Column names normalized to `snake_case`.
  - Duplicates removed by row or business key strategy.
  - Missing values handled according to the configured strategy.
  - Best-effort dtype normalization for numeric, datetime, and categorical fields.

### Gold
- Purpose: provide dashboard-ready business outputs and stable downstream contracts.
- Minimum schema required by tests:
  - `metric_name` (`string`, non-null)
  - `metric_value` (`numeric`, non-null)
  - `segment` (`string`, non-null)
  - `reference_date` (datetime-like, non-null)
- Quality rules:
  - `metric_name` + `segment` + `reference_date` must be unique.
  - `metric_value` must be finite.
  - Gold output must contain at least one row.

## Validation Strategy
- Unit tests validate Gold schema and quality constraints.
- CI blocks merges when contract checks fail.
- The contract is intentionally strict at the Gold layer and intentionally lighter upstream.
