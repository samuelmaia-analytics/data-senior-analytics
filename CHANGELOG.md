# Changelog

All notable changes to this project are documented in this file.

## [1.0.0] - 2026-03-04
### Release Highlights
- End-to-end executive analytics workflow with recruiter-first documentation.
- Senior engineering quality gates (lint, tests, coverage, contracts).
- Architecture evidence package (ADR + data contract + lineage controls).
- Demo: https://data-analytics-sr.streamlit.app

### Added
- Recruiter-first README upgrades: executive summary, impact section, architecture links, and demo screenshots.
- CI coverage flow with `pytest-cov` and Codecov upload.
- Tooling hardening via `ruff`, `black`, optional `mypy`, and pre-commit integration.
- Makefile workflow: `make setup`, `make lint`, `make test`, `make run`.
- Architecture proof documents: layered architecture, ADR, and data contract.
- Output contract tests for Gold analytics artifacts.
- Repository metadata files: MIT `LICENSE` and `.env.example` documentation references.

### Changed
- Pytest now enforces coverage threshold (`>=70%`).
- CI now runs formatter checks and publishes `coverage.xml`.
