# Architecture Overview

## System Architecture

MarketSensing follows a **medallion architecture** (Bronze → Silver → Gold) built on Azure + Databricks.

### Data Flow

```
External Sources → Ingestion (Stream/Batch) → Bronze (Raw)
    → Silver (Cleaned) → Gold (Features) → Signal Models
    → Orchestrator → Signal Book → API / Dashboards
```

### Key Design Decisions

1. **Medallion pattern** for data quality progression and replayability
2. **Feature Store** as the single interface between data engineering and signal models
3. **Configuration-driven signals** — all thresholds, windows, and limits in YAML
4. **Signal-first architecture** — no execution coupling in v1; clean interface for future OMS

### Latency Tiers

| Tier | Latency | Use Case |
|------|---------|----------|
| Fast | 1-30 seconds | NYMEX futures spread signals |
| Medium | 1-5 minutes | Physical hub basis signals |
| Slow | 15-60 minutes | Fundamental/inventory-driven signals |

### Data Lineage

Every signal carries full provenance:
```
raw_event → bronze_record → silver_record → feature_vector → model_version → signal
```

All stages are immutable and queryable for audit.

## Component Responsibilities

### Ingestion Layer
- **Streaming**: Event Hubs consumers for NYMEX tick data, physical price feeds
- **Batch**: ADF pipelines for EIA reports, Baker Hughes rig counts, weather data
- **Schema Registry**: Avro/JSON schema validation at ingestion boundary

### Feature Engineering
- Operates on Silver/Gold Delta tables
- Produces time-indexed, instrument-indexed feature vectors
- Materialized to Feature Store for training and live scoring

### Signal Models
- Rules-based: stateless threshold evaluation
- ML-based: stateful models (regime detection, mean-reversion)
- Risk filters: position limits, event kill-switches, correlation checks

### Orchestrator
- Merges signals across strategies for the same instrument
- Resolves conflicts (opposing signals from different models)
- Applies portfolio-level risk constraints
- Produces the final Signal Book

### Monitoring
- Backtesting engine for historical signal evaluation
- Real-time P&L tracking per signal and strategy
- Signal health dashboards with decay detection
