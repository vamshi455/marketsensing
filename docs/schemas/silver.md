# Silver Layer Schemas (Cleaned & Conformed)

Deduplicated, validated, and standardized data.

## `silver.prices`

Unified price table for all instruments (futures + physical).

| Column | Type | Description |
|--------|------|-------------|
| `trade_date` | DATE | Trading date |
| `timestamp` | TIMESTAMP | Event timestamp |
| `instrument_id` | STRING | Standardized instrument ID |
| `price_type` | STRING | settlement, assessment, trade, quote |
| `open` | DOUBLE | Open price (futures) or NULL |
| `high` | DOUBLE | High price |
| `low` | DOUBLE | Low price |
| `close` | DOUBLE | Close/settlement price |
| `volume` | LONG | Volume (contracts or barrels) |
| `open_interest` | LONG | Open interest (futures only) |
| `source` | STRING | Data provider |
| `quality_flag` | STRING | ok, interpolated, stale, missing |

**Partition**: `trade_date`, `instrument_id`
**Z-ORDER**: `instrument_id`, `timestamp`

## `silver.eia_inventory`

| Column | Type | Description |
|--------|------|-------------|
| `report_date` | DATE | Report publication date |
| `period_ending` | DATE | Data period end date |
| `metric` | STRING | us_crude_stocks, cushing_stocks, etc. |
| `value` | DOUBLE | Actual value |
| `unit` | STRING | thousand_barrels, pct, etc. |
| `prior_value` | DOUBLE | Previous period value |
| `change` | DOUBLE | Period-over-period change |
| `forecast_value` | DOUBLE | Consensus forecast (if available) |
| `surprise` | DOUBLE | actual - forecast |

**Partition**: `report_date`

## `silver.rig_counts`

| Column | Type | Description |
|--------|------|-------------|
| `report_date` | DATE | Report date |
| `basin` | STRING | Basin name |
| `rig_type` | STRING | oil, gas |
| `count` | INT | Active rig count |
| `prior_count` | INT | Previous week count |
| `change` | INT | Week-over-week change |

**Partition**: `report_date`

## `silver.events_calendar`

| Column | Type | Description |
|--------|------|-------------|
| `event_date` | DATE | Event date |
| `event_time` | STRING | Scheduled time (ET) |
| `event_type` | STRING | eia_crude, eia_gas, fomc, etc. |
| `impact` | STRING | high, medium, low |
| `description` | STRING | Event description |
| `status` | STRING | scheduled, released, cancelled |

**Partition**: `event_date`
