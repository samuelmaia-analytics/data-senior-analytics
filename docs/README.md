# Documentation Index

This folder consolidates the technical, operational, and governance narrative behind the project.

## Recommended Reading Path
1. [ARCHITECTURE.md](ARCHITECTURE.md)
2. [STREAMLIT_CLOUD.md](STREAMLIT_CLOUD.md)
3. [DATA_CONTRACT.md](DATA_CONTRACT.md)
4. [DATA_PROVENANCE.md](DATA_PROVENANCE.md)
5. [DATA_LINEAGE.md](DATA_LINEAGE.md)

## Core Documents
- [ARCHITECTURE.md](ARCHITECTURE.md): layered design, operating model, and system flow.
- [STREAMLIT_CLOUD.md](STREAMLIT_CLOUD.md): deployment contract, runtime guardrails, and troubleshooting.
- [DATA_CONTRACT.md](DATA_CONTRACT.md): expected guarantees for raw, bronze, silver, and gold outputs.
- [DATA_PROVENANCE.md](DATA_PROVENANCE.md): source governance, traceability, and release requirements.
- [DATA_LINEAGE.md](DATA_LINEAGE.md): reproducibility strategy and manifest-based lineage tracking.

## What Changed in the Current Product Surface
- The dashboard now exposes a decision brief, trust level, and release posture in `Overview`.
- Governance is visible in the UI through freshness, source, transformation count, and quality status.
- The analytics layer now produces both business concentration signals and operational confidence signals.

## ADRs
- [ADR-0001-streamlit-presentation-layer.md](adr/ADR-0001-streamlit-presentation-layer.md)
- [ADR-0002-sqlite-persistence.md](adr/ADR-0002-sqlite-persistence.md)
- [ADR-0003-kaggle-provenance-gate.md](adr/ADR-0003-kaggle-provenance-gate.md)

## Documentation Standard
- Prefer operational clarity over generic description.
- Keep business-facing language explicit when a document influences decision-making.
- Keep runtime, data quality, and governance guidance aligned with the deployed system.
