# Gold Layer Schemas (Features & Aggregates)

Pre-computed features optimized for signal model scoring.

## `gold.price_bars`

Resampled OHLCV bars at multiple frequencies.

| Column | Type | Description |
|--------|------|-------------|
| `instrument_id` | STRING | Instrument identifier |
| `bar_timestamp` | TIMESTAMP | Bar start time |
| `frequency` | STRING | 1m, 5m, 15m, 1h, 1d |
| `open` | DOUBLE | Open price |
| `high` | DOUBLE | High price |
| `low` | DOUBLE | Low price |
| `close` | DOUBLE | Close price |
| `volume` | LONG | Total volume |
| `vwap` | DOUBLE | Volume-weighted average price |
| `trade_count` | INT | Number of trades |

**Partition**: `frequency`, `trade_date`
**Z-ORDER**: `instrument_id`, `bar_timestamp`

## `gold.spreads`

Pre-computed spread values for all configured pairs.

| Column | Type | Description |
|--------|------|-------------|
| `spread_id` | STRING | Strategy/spread identifier |
| `timestamp` | TIMESTAMP | Calculation timestamp |
| `trade_date` | DATE | Trading date |
| `instrument_long` | STRING | Long leg instrument |
| `instrument_short` | STRING | Short leg instrument |
| `spread_type` | STRING | location, time, crack |
| `spread_value` | DOUBLE | Raw spread (long - short) |
| `spread_pct` | DOUBLE | Spread as percentage |
| `rolling_mean` | DOUBLE | Rolling mean (lookback window) |
| `rolling_std` | DOUBLE | Rolling std deviation |
| `z_score` | DOUBLE | (spread - mean) / std |
| `percentile_rank` | DOUBLE | Historical percentile (0-100) |

**Partition**: `trade_date`
**Z-ORDER**: `spread_id`, `timestamp`

## `gold.technical_indicators`

| Column | Type | Description |
|--------|------|-------------|
| `instrument_id` | STRING | Instrument identifier |
| `timestamp` | TIMESTAMP | Calculation timestamp |
| `trade_date` | DATE | Trading date |
| `sma_10` | DOUBLE | 10-period simple moving average |
| `sma_20` | DOUBLE | 20-period SMA |
| `sma_50` | DOUBLE | 50-period SMA |
| `ema_12` | DOUBLE | 12-period exponential MA |
| `ema_26` | DOUBLE | 26-period EMA |
| `rsi_14` | DOUBLE | 14-period RSI |
| `atr_14` | DOUBLE | 14-period Average True Range |
| `bbands_upper` | DOUBLE | Bollinger upper (20, 2σ) |
| `bbands_lower` | DOUBLE | Bollinger lower (20, 2σ) |
| `realized_vol_20` | DOUBLE | 20-day realized volatility |
| `realized_vol_60` | DOUBLE | 60-day realized volatility |

**Partition**: `trade_date`
**Z-ORDER**: `instrument_id`

## `gold.fundamental_features`

| Column | Type | Description |
|--------|------|-------------|
| `trade_date` | DATE | Feature date |
| `inventory_surprise_crude` | DOUBLE | EIA crude actual - forecast |
| `cushing_utilization_pct` | DOUBLE | Cushing storage % utilized |
| `cushing_stocks_change` | DOUBLE | Week-over-week change |
| `us_crude_days_supply` | DOUBLE | Days of supply at current demand |
| `rig_count_change` | INT | Week-over-week rig count delta |
| `permian_rig_count` | INT | Permian basin active rigs |
| `seasonal_flag` | STRING | driving_season, winter, shoulder |
| `days_to_next_eia` | INT | Business days until next EIA report |
| `hurricane_risk_flag` | BOOLEAN | Active Gulf Coast hurricane threat |

**Partition**: `trade_date`

## `gold.signals`

Generated trading signals (the Signal Book).

| Column | Type | Description |
|--------|------|-------------|
| `signal_id` | STRING | UUID |
| `timestamp` | TIMESTAMP | Signal generation time |
| `strategy_id` | STRING | Strategy identifier |
| `instrument_long` | STRING | Long leg |
| `instrument_short` | STRING | Short leg (nullable) |
| `action` | STRING | enter, exit |
| `side` | STRING | long_spread, short_spread, long, short |
| `size` | DOUBLE | Recommended size (contracts) |
| `confidence` | DOUBLE | Model confidence (0.0-1.0) |
| `expected_hold_time` | STRING | Expected hold duration |
| `rationale` | STRING | Human-readable explanation |
| `model_version` | STRING | Model/strategy version |
| `risk_checks_passed` | BOOLEAN | All risk filters passed |
| `regime` | STRING | Current detected market regime |
| `features_snapshot` | STRING | JSON of key input features |
| `status` | STRING | active, expired, executed, cancelled |
| `pnl_realized` | DOUBLE | Realized P&L (filled post-exit) |

**Partition**: `trade_date`
**Z-ORDER**: `strategy_id`, `timestamp`
