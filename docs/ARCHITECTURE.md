# Architecture

## Summary
The project uses a layered analytics architecture to turn raw tabular inputs into curated, decision-ready outputs. The Streamlit dashboard is the product surface, but the design intentionally separates curation, profiling, business scoring, governance signaling, persistence, and operational controls.

## Architectural Intent
- Preserve a clean boundary between UI concerns and analytical workflow orchestration.
- Convert data quality into explicit release and decision signals.
- Keep curation reusable outside the dashboard.
- Make deployment and governance first-class parts of the system.
- Expose decision risk, confidence, and release posture directly in the UI.

## Layers
- Presentation layer: `dashboard/app.py` renders the interface, KPI surfaces, EDA tabs, and persistence actions.
- Dashboard analytics layer: `dashboard/utils/analytics.py` translates profiling into quality score, priority actions, business snapshot, governance snapshot, decision brief, and correlation summaries.
- Application service layer: `src/app/curation_service.py` orchestrates curation, profiling, scoring, and business metadata generation.
- Domain analytics layer: `src/analysis/exploratory.py` generates descriptive statistics and automated insights.
- Data curation layer: `src/data/transformer.py` standardizes column names, infers types, handles missing values, and removes duplicates.
- Persistence layer: `src/data/sqlite_manager.py` stores curated outputs in SQLite for downstream inspection and reuse.
- Platform/config layer: `config/settings.py`, `config/dashboard_policy.json`, `.streamlit/`, and validation scripts define runtime paths, scoring policies, deployment expectations, and governance checks.

## End-to-End Flow
```mermaid
flowchart LR
    A[Raw CSV / XLSX / Demo data] --> B[Streamlit upload or auto-load]
    B --> C[Curation service]
    C --> D[Curated DataFrame]
    D --> E[ExploratoryAnalyzer]
    D --> F[Business score + snapshot]
    D --> G[(SQLite)]
    E --> H[EDA + diagnostics]
    F --> I[Decision dashboard]
```

## Runtime Sequence
```mermaid
sequenceDiagram
    participant U as User
    participant UI as Streamlit UI
    participant AP as Curation Service
    participant TR as DataTransformer
    participant AN as ExploratoryAnalyzer
    participant AU as Dashboard Analytics Utils
    participant DB as SQLiteManager

    U->>UI: Upload CSV/XLSX or load demo dataset
    UI->>AP: Start curation workflow
    AP->>TR: Standardize, infer, impute, deduplicate
    TR-->>AP: Curated DataFrame + transformation log
    AP->>AN: Produce statistics and automated insights
    AN-->>AP: Analytical profile
    AP->>AU: Build quality summary, business snapshot, and governance signals
    AU-->>UI: KPI, decision brief, release posture, priority actions
    UI->>DB: Persist curated dataset (optional)
    DB-->>UI: Queryable analytical tables
```

## Dashboard Operating Model
- `Overview`: KPI, decision brief, confidence level, release posture, commercial concentration, and trend view.
- `Upload`: raw-to-curated transition with immediate quality feedback.
- `Data`: raw vs. curated inspection, column profile, and transformation log.
- `EDA`: automated insights, descriptive statistics, missing profile, and strongest correlations.
- `Visualizations`: distribution analysis, business mix, and time trend exploration.
- `Database`: operational confirmation of persisted curated data.
- `Settings`: runtime metadata, governance metadata, quality metadata, and transformation count.

## Engineering Controls
- CI gate: lint, format, tests, and coverage (`>=70%`).
- Streamlit Cloud preflight and runtime runbook in [STREAMLIT_CLOUD.md](STREAMLIT_CLOUD.md).
- Structured logs with `trace_id` and per-page elapsed time.
- Manifest and provenance checks to reduce silent data drift.
- Smoke tests that render dashboard pages in CI.
