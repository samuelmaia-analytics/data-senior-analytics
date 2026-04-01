# ADR-0004 Privacy And Retention Controls

## Status
Accepted

## Context
The dashboard accepts user uploads and can persist curated outputs into SQLite. Once personal data indicators were introduced into the product surface, persistence could no longer be treated as a neutral operation.

The project needed controls that:
- reduce exposure of direct identifiers in the interface
- make privacy risk explicit before persistence
- track retention and persistence mode over time
- leave an auditable trace for governance review

## Decision
The project adopts the following controls:
- mask previews when personal data indicators are detected
- default to masked persistence when personal data is present
- require explicit acknowledgement before persisting personal data
- register persistence metadata in SQLite
- assign retention at persistence time
- purge expired datasets automatically when the dashboard loads
- record persistence and purge events in an audit log

## Consequences
### Positive
- Privacy risk becomes visible in the product surface.
- Persistence is governed by metadata rather than left implicit.
- Retention becomes operational instead of merely documented.
- The repository signals stronger engineering maturity for analytics governance.

### Negative
- Detection is heuristic and can produce false positives or false negatives.
- Automatic purge on app load is a pragmatic control, not a replacement for a dedicated scheduler.
- This remains an engineering control set, not legal compliance by itself.

## Alternatives Considered
- Persist everything and rely only on documentation: rejected.
- Block all persistence when personal data is detected: too rigid for the current scope.
- Add a full identity and approval workflow now: postponed as a later product step.
