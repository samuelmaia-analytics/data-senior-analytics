# Architecture

## Executive Summary
The project follows a layered analytics architecture to keep business UI concerns separate from data processing and persistence.

## Layered Approach
- Presentation layer: `dashboard/app.py` and `dashboard/utils/*` for UX, charts, and KPI communication.
- Application layer: orchestration inside the Streamlit flow (upload, validation, pipeline execution).
- Domain analytics layer: `src/analysis/exploratory.py` and `src/data/transformer.py` for statistical logic and transformations.
- Data access layer: `src/data/file_extractor.py` and `src/data/sqlite_manager.py` for ingestion and persistence.
- Platform/config layer: `config/settings.py`, `config/data_source.yaml`, and validation scripts.

## End-to-End Flow
```mermaid
flowchart LR
    A[Raw CSV/XLSX] --> B[Raw Validation]
    B --> C[Bronze: Standardized ingest]
    C --> D[Silver: Cleaned and typed]
    D --> E[Gold: Business KPIs and aggregates]
    E --> F[Dashboard + executive insights]
    D --> G[(SQLite)]
    E --> G
```

## Runtime Sequence
```mermaid
sequenceDiagram
    participant U as User
    participant UI as Streamlit UI
    participant FE as FileExtractor
    participant TR as DataTransformer
    participant AN as ExploratoryAnalyzer
    participant DB as SQLiteManager

    U->>UI: Upload CSV/XLSX
    UI->>FE: Read file
    FE-->>UI: Raw DataFrame
    UI->>TR: Clean columns, fill missing, deduplicate
    TR-->>UI: Silver DataFrame
    UI->>AN: Analyze + summarize
    AN-->>UI: Gold-ready metrics/insights
    UI->>DB: Persist curated outputs
    DB-->>UI: Queryable analytical tables
```

## Evidence of Engineering Discipline
- CI gate: lint + format + tests + coverage (`>=70%`).
- Data contract and output contract tests for predictable Gold outputs.
- ADR folder to document architecture decisions.
