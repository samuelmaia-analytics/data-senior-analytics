# Architecture

## Executive Summary
The project follows a layered analytics architecture that separates business presentation, curation logic, exploratory analysis, and persistence. The dashboard is not only a UI shell: it orchestrates a governed path from raw upload to curated, decision-ready output.

## Layers
- Presentation layer: `dashboard/app.py` renders the executive experience, KPI cards, EDA tabs, and persistence flows.
- Dashboard analytics layer: `dashboard/utils/analytics.py` converts technical profiling into executive metrics such as quality score, priority actions, and board-ready snapshots.
- Domain analytics layer: `src/analysis/exploratory.py` produces descriptive statistics and automated insights.
- Data curation layer: `src/data/transformer.py` standardizes columns, infers types, treats missing values, and removes duplicates.
- Persistence layer: `src/data/sqlite_manager.py` stores curated datasets in SQLite for downstream querying.
- Platform/config layer: `config/settings.py`, `.streamlit/`, and validation scripts define runtime paths, deployment guardrails, and governance checks.

## End-to-End Flow
```mermaid
flowchart LR
    A[Raw CSV / XLSX / Demo data] --> B[Streamlit upload or auto-load]
    B --> C[DataTransformer]
    C --> D[Curated DataFrame]
    D --> E[ExploratoryAnalyzer]
    D --> F[Executive Snapshot + Quality Score]
    D --> G[(SQLite)]
    E --> H[EDA tabs + diagnostics]
    F --> I[Executive summary + board briefing]
```

## Runtime Sequence
```mermaid
sequenceDiagram
    participant U as User
    participant UI as Streamlit UI
    participant TR as DataTransformer
    participant AN as ExploratoryAnalyzer
    participant AU as Dashboard Analytics Utils
    participant DB as SQLiteManager

    U->>UI: Load demo or upload CSV/XLSX
    UI->>TR: Curate raw DataFrame
    TR-->>UI: Clean, typed, deduplicated DataFrame
    UI->>AN: Profile and analyze curated data
    AN-->>UI: Stats and automated insights
    UI->>AU: Build quality summary and executive snapshot
    AU-->>UI: KPI, quality score, priority actions
    UI->>DB: Persist curated output (optional)
    DB-->>UI: Queryable analytical tables
```

## Dashboard Operating Model
- `Overview`: executive KPI, quality status, board briefing, top category, top region, revenue trend.
- `Upload`: raw-to-curated flow, quality gate visibility, and persistence to SQLite.
- `Data`: curated preview, raw preview, column profile, and transformation log.
- `EDA`: insights, statistics, missing profile, and strongest correlations.
- `Visualizations`: distribution, business mix, and trend analysis.
- `Database`: operational verification of persisted analytical tables.
- `Settings`: runtime metadata, quality metadata, and transformation count.

## Engineering Discipline
- CI gate: lint + format + tests + coverage (`>=70%`).
- Streamlit Cloud preflight and deployment runbook in `docs/STREAMLIT_CLOUD.md`.
- Structured logs with `trace_id` and per-page elapsed time.
- Data provenance and manifest checks to prevent silent drift.
- ADRs to document major architectural decisions.
