# Persistence Module

Data storage layer using Delta Lake (medallion architecture) and Snowflake.

## Responsibilities
- Manage Bronze / Silver / Gold Delta Lake tables
- Schema enforcement and evolution
- Read/write interfaces for features, signals, and audit logs
- Snowflake sync for analytics and reporting

## Medallion Layers

### Bronze (Raw)
- Immutable append-only raw events
- Partitioned by `ingestion_date` and `source`
- No transformations, full fidelity

### Silver (Cleaned)
- Deduplication, null handling, type casting
- Standardized column names and units
- Partitioned by `trade_date` and `instrument_id`

### Gold (Features & Aggregates)
- Feature store tables (time + instrument indexed)
- Pre-computed spreads, indicators, and aggregates
- Optimized for model scoring queries
