# Contributing Guide

This repository follows a practical engineering workflow focused on traceability, quality, and reproducibility.

## Branch Strategy
- `main`: protected branch for stable releases.
- Feature branches: `feat/<short-topic>`, `fix/<short-topic>`, `chore/<short-topic>`.

Examples:
- `feat/gold-output-contract-tests`
- `fix/ci-black-format-check`
- `chore/docs-architecture-index`

## Commit Convention
Use small, atomic commits with clear intent.

Format:
`<type>: <objective>`

Types:
- `feat`: new behavior or capability
- `fix`: bug fix or regression fix
- `refactor`: code change without behavior change
- `test`: tests added/updated
- `docs`: documentation only
- `chore`: tooling, CI, config, maintenance

Good examples:
- `feat: add output contract tests for gold layer`
- `fix: handle missing values in auto strategy for categorical columns`
- `docs: add architecture decision index`
- `chore: enforce coverage gate in pytest config`

## Pull Request Rules
Each PR should be focused and easy to review.

Required:
- Clear problem statement and scope
- Risk and rollback notes
- Validation evidence (commands + outputs summary)
- Updated docs when behavior/contracts change

## Quality Checklist
Run before opening PR:

```bash
make lint
make test
python scripts/check_encoding.py
python scripts/streamlit_cloud_preflight.py
python scripts/validate_data_provenance.py
python scripts/generate_data_manifest.py --check
python scripts/check_secrets.py
```

## Data and Contract Governance
When changing pipeline outputs:
- Update `docs/DATA_CONTRACT.md` if schema/quality rules change.
- Regenerate `docs/data_manifest.json` via `python scripts/generate_data_manifest.py` when versioned data files change.
- Add or update output contract tests in `tests/`.
- Ensure no raw sensitive data is committed.

## Documentation Expectations
Any architecture or behavior change should include at least one:
- Update in `docs/ARCHITECTURE.md`
- ADR update/addition in `docs/adr/`
- Changelog entry in `CHANGELOG.md`
