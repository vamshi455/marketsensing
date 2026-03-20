# Bronze Layer Schemas (Raw)

Immutable, append-only raw events. No transformations applied.

## `bronze.market_ticks`

| Column | Type | Description |
|--------|------|-------------|
| `ingestion_ts` | TIMESTAMP | When the record was ingested |
| `source` | STRING | Data source identifier |
| `instrument_id` | STRING | Instrument identifier |
| `exchange` | STRING | Exchange code (e.g., NYMEX) |
| `price` | DOUBLE | Trade/quote price |
| `volume` | LONG | Trade volume (contracts) |
| `bid` | DOUBLE | Best bid |
| `ask` | DOUBLE | Best ask |
| `event_type` | STRING | trade, quote, settlement |
| `raw_payload` | STRING | Original JSON/FIX message |

**Partition**: `ingestion_date`, `source`

## `bronze.physical_assessments`

| Column | Type | Description |
|--------|------|-------------|
| `ingestion_ts` | TIMESTAMP | When the record was ingested |
| `source` | STRING | Provider (platts, argus) |
| `assessment_date` | DATE | Assessment date |
| `instrument_id` | STRING | Hub identifier |
| `price_low` | DOUBLE | Assessment range low |
| `price_high` | DOUBLE | Assessment range high |
| `price_mid` | DOUBLE | Midpoint assessment |
| `unit` | STRING | Price unit (USD/bbl) |
| `raw_payload` | STRING | Original record |

**Partition**: `ingestion_date`, `source`

## `bronze.eia_reports`

| Column | Type | Description |
|--------|------|-------------|
| `ingestion_ts` | TIMESTAMP | When ingested |
| `report_type` | STRING | crude_inventory, gas_storage |
| `report_date` | DATE | Report reference date |
| `period_ending` | DATE | Data period end date |
| `series_id` | STRING | EIA series identifier |
| `value` | DOUBLE | Reported value |
| `unit` | STRING | Unit (thousand barrels, etc.) |
| `raw_payload` | STRING | Original API response |

**Partition**: `ingestion_date`, `report_type`

## `bronze.rig_counts`

| Column | Type | Description |
|--------|------|-------------|
| `ingestion_ts` | TIMESTAMP | When ingested |
| `report_date` | DATE | Report date |
| `basin` | STRING | Basin name (Permian, Eagle Ford, etc.) |
| `rig_type` | STRING | oil, gas, misc |
| `count` | INT | Active rig count |
| `raw_payload` | STRING | Original record |

**Partition**: `ingestion_date`
