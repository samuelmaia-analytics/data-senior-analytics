# Documentation Index

This folder centralizes the technical and operational narrative behind the executive analytics dashboard.

## Core Documents
- [ARCHITECTURE.md](ARCHITECTURE.md): layered design, runtime flow, and dashboard operating model.
- [STREAMLIT_CLOUD.md](STREAMLIT_CLOUD.md): deployment runbook, Python/runtime guardrails, and smoke test checklist.
- [DATA_CONTRACT.md](DATA_CONTRACT.md): raw/bronze/silver/gold expectations and output rules.
- [DATA_LINEAGE.md](DATA_LINEAGE.md): lineage manifest and reproducibility process.
- [DATA_PROVENANCE.md](DATA_PROVENANCE.md): dataset source governance and approval rules.

## ADRs
- [ADR-0001-streamlit-presentation-layer.md](adr/ADR-0001-streamlit-presentation-layer.md)
- [ADR-0002-sqlite-persistence.md](adr/ADR-0002-sqlite-persistence.md)
- [ADR-0003-kaggle-provenance-gate.md](adr/ADR-0003-kaggle-provenance-gate.md)

## Recommended Reading Order
1. Start with [ARCHITECTURE.md](ARCHITECTURE.md).
2. Review [STREAMLIT_CLOUD.md](STREAMLIT_CLOUD.md) for runtime/deploy operations.
3. Confirm data governance in [DATA_PROVENANCE.md](DATA_PROVENANCE.md) and [DATA_CONTRACT.md](DATA_CONTRACT.md).
