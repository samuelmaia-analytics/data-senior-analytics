# Architecture

## Context
This project targets executive-level analytics delivery with clear governance, reproducibility, and fast deployment on Streamlit Cloud.

## System View
```mermaid
flowchart TD
    U[Business user] --> A[Streamlit UI dashboard/app.py]
    A --> B[Ingestion file_extractor.py]
    A --> C[Transformation transformer.py]
    A --> D[EDA exploratory.py]
    A --> E[Persistence sqlite_manager.py]
    E --> F[(SQLite analytics.db)]
    D --> G[Executive insights]
    C --> G
```

## Runtime Sequence
```mermaid
sequenceDiagram
    participant User
    participant UI as Streamlit UI
    participant Ingest as FileExtractor
    participant Transform as DataTransformer
    participant Analyze as ExploratoryAnalyzer
    participant DB as SQLiteManager

    User->>UI: Upload CSV/XLSX
    UI->>Ingest: Read file + detect encoding
    Ingest-->>UI: DataFrame
    UI->>Transform: Clean and enrich
    Transform-->>UI: Processed DataFrame
    UI->>Analyze: Run EDA and statistics
    Analyze-->>UI: Metrics and insights
    UI->>DB: Save/read analytical tables
    DB-->>UI: Persisted results
    UI-->>User: Visual narratives + KPIs
```

## Module Boundaries
- `dashboard/app.py`: orchestration and routing.
- `dashboard/pages/*`: page-level rendering logic.
- `dashboard/utils/*`: shared analytical helpers for pages.
- `src/data/*`: ingestion, transformations, persistence.
- `src/analysis/*`: exploratory analytics and report generation.
- `config/*`: settings and data provenance.

## Quality Controls
- Lint: `ruff`
- Tests: `pytest`
- Encoding guard: `scripts/check_encoding.py`
- Cloud preflight: `scripts/streamlit_cloud_preflight.py`
- Data provenance validation: `scripts/validate_data_provenance.py`
