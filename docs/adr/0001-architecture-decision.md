# ADR 0001: Layered Analytics Architecture

- Status: Accepted
- Date: 2026-03-04

## Context
The project must support recruiter visibility and production-grade maintainability while keeping local execution lightweight.

## Decision
Adopt a layered architecture:
- Presentation: Streamlit dashboard
- Domain analytics: transformation + exploratory/statistical logic
- Data access: ingestion + SQLite persistence
- Platform/config: settings, provenance, quality gates

## Consequences
- Improves testability and traceability.
- Supports explicit data contracts and output contract tests.
- Enables independent evolution of UI and data layers.

## Related ADRs
- [ADR-0001-streamlit-presentation-layer.md](ADR-0001-streamlit-presentation-layer.md)
- [ADR-0002-sqlite-persistence.md](ADR-0002-sqlite-persistence.md)
- [ADR-0003-kaggle-provenance-gate.md](ADR-0003-kaggle-provenance-gate.md)
