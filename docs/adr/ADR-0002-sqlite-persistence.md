# ADR-0002: SQLite for Analytical Persistence

## Status
Accepted

## Context
The project needs local reproducibility and simple persistence for demo and cloud scenarios.

## Decision
Use SQLite through `sqlite_manager.py` for analytical table storage.

## Consequences
- Positive: zero external dependency, easy portability, low setup cost.
- Negative: limited concurrency and scale compared to warehouse solutions.
