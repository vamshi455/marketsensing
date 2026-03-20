# ADR-001: Medallion Architecture for Data Storage

## Status
Accepted

## Context
We need a data architecture that supports:
- Full auditability and lineage from raw data to signals
- Replayability for backtesting
- Separation of concerns between raw ingestion, cleaning, and feature computation

## Decision
Adopt the **Bronze → Silver → Gold** medallion architecture on Delta Lake.

- **Bronze**: immutable raw events, append-only, no transformations
- **Silver**: cleaned, deduplicated, standardized records
- **Gold**: pre-computed features and aggregates optimized for model scoring

## Consequences
- Storage costs increase due to data duplication across layers
- Clear lineage and easy debugging of data quality issues
- Backfills can reprocess from Bronze without re-ingesting
- Feature store queries run against optimized Gold tables
