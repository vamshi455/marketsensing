# Data Model Reference

**Purpose**: Comprehensive data model documentation for the MarketSensing platform. All personal identifiers and company-specific references have been removed.

---

## Data Categories (Modeling Buckets)

The system ingests and models data across seven primary business categories:

| Category | Description | Examples |
|----------|---|---|
| **Supply** | Refinery production, imports, exports | Production volumes, competitor output, flows |
| **Demand** | Sales and consumption of products | Customer demand, market consumption rates |
| **Inventory** | Static storage and in-transit volumes | Tank levels, pipeline volumes, storage positions |
| **Production Costs** | Refining and storage expenses | Per-barrel refining costs, storage fees |
| **Transport Costs** | Logistics and movement expenses | Pipeline rates, barge fees, vessel charters |
| **Macroeconomic** | Broader economic indicators | CPI, S&P 500, FX rates, interest rates |
| **External/Environmental** | Non-commodity external data | Weather (temperature, precipitation), geopolitical events |

---

## Data Sources (18+)

### Market & Exchange Data
- **NYMEX** — Futures exchange data (WTI, RBOB, ULSD); real-time tick data
- **Platts/Argus** — Physical hub price assessments (Midland, Cushing, Houston); daily updates
- **CFTC** — Commitment of Traders reports; weekly positioning data

### Third-Party Analytics & Intelligence
- **Kpler** — Commercial tanker tracking; real-time vessel movements and trade flows
- **Genscape** — Real-time refinery operations and utilization metrics
- **Enverus** — Upstream production data and rig count trends
- **WoodMac** — Long-term commodity forecasts and market outlooks
- **Market Intelligence Provider** — News feeds, sentiment data, market analysis

### Public Data Services
- **EIA** — US Energy Information Administration; weekly inventory, production, refinery runs
- **Weather Service** — Temperature, precipitation, wind data for demand modeling

### Internal Operational Systems (Generic Names)
- **Internal Production Forecasts DB** — Refinery production predictions 1-3 weeks ahead
- **Internal Sales Forecasts DB** — Demand forecasts by customer segment and geography
- **Transportation Cost Index** — Pipeline, barge, and vessel rate tracking
- **Maintenance Schedule DB** — Refinery turnaround and maintenance calendars
- **Deal Tracking System** — Executed trades, deal structures, margins
- **Risk Tracking Dashboard** — Positions, P&L, portfolio constraints, exposure limits

---

## Data Ingestion Patterns

### Real-Time Sources (Sub-minute to hourly)
- NYMEX futures ticks
- Genscape refinery operations
- Tanker vessel movements (Kpler)
- Weather observations

### Daily Sources
- Platts/Argus physical assessments
- Kpler daily summaries
- Enverus production updates
- Internal forecasts refresh

### Weekly Sources
- EIA inventory reports (Wednesday 10:30 AM ET)
- CFTC positioning reports
- WoodMac market analysis updates

### As-Needed Sources
- Maintenance schedule updates (event-driven)
- Internal risk position updates (real-time snapshots)

---

## Data Architecture (Medallion Pattern)

### Bronze Layer (Raw Events)
- Raw, unprocessed data from 18+ sources
- 213+ tables total
- Append-only, partitioned by ingestion_date
- No transformations or cleaning

**Purpose**: Immutable source-of-truth backup

### Silver Layer (Cleaned & Standardized)
- Deduplicated records
- Type-casted to target schemas
- Null value handling
- Standardized naming conventions
- Business logic applied

**Purpose**: Clean data for feature engineering

### Gold Layer (Features & Aggregates)
- 100+ pre-computed features
- Indexed by: commodity + contract + time
- Optimized for model inference
- Time-series aligned (hourly, daily, weekly resampling)

**Purpose**: Ready-for-model feature sets

---

## Feature Categories (100+ Total)

### Time Series Features
- OHLCV bars (open, high, low, close, volume)
- Resampling to multiple timeframes (1h, 1d, 1w)
- Alignment across commodities

### Spread Features
- **Time Spreads**: Near-term vs far-term prices (F1-F3, F1-F6, F1-F12)
- **Geographic Spreads**: Hub-to-hub (Midland vs Cushing, etc.)
- **Crack Spreads**: 3:2:1 ratio (RBOB + ULSD vs WTI)

### Technical Indicators
- Moving averages (MA): 7-day, 14-day, 30-day, 60-day exponential
- Momentum: RSI (14-day), rate of change
- Volatility: 20-day rolling standard deviation
- Z-scores: Normalized spread deviations from 60-day mean
- Bollinger Bands: Upper/lower confidence bands

### Fundamental Features
- **Supply Drivers**: Production volumes, refinery utilization, turnaround impacts
- **Demand Drivers**: Sales forecast vs actual, customer segment activity
- **Inventory Effects**: Days of supply, in-transit volumes, storage levels
- **Costs**: Production per-barrel, transport rates, storage fees

### Macroeconomic Features
- CPI and inflation indicators
- Energy prices (crude, natural gas)
- FX rates (USD index, EURUSD)
- Bond yields and interest rates
- Economic sentiment indices

### Weather Impact Features
- Temperature deviations from seasonal normal
- Heating/cooling degree days
- Precipitation and drought conditions
- Hurricane and storm tracking

---

## Modeling Approach

### Model Type
- **LightGBM Regressor** (gradient boosting decision trees)
- Not rules-based; data-driven predictions

### Model Dimensions
- **50+ models in production** (phase 1)
  - 7 leap durations: 1d, 3d, 7d, 14d, 30d, 60d, 90d
  - 12 commodities (phased rollout)
  - One regressor per leap-duration-commodity combination

### Target Variable
- Spread value at future anchor date
- Example: "WTI F1-F3 spread value on 2026-09-15"

### Input Features
- 100+ features from all categories above
- 60-day historical lookback
- Fundamentals + technical + macro + weather

### Model Output
- Continuous regression prediction (expected spread value)
- Thresholding → BUY/SELL/NEUTRAL classification
- Confidence scoring via prediction confidence intervals

### Evaluation Metrics
- **Regression**: R², MAE (mean absolute error), RMSE (root mean squared error)
- **Classification**: Precision (63% historical), Recall, F1-score
- **Trading**: Sharpe ratio (1.94x historical), P&L attribution, drawdown analysis
- **Backtesting**: Walk-forward validation with realistic slippage and bid-ask

---

## Data Flow Architecture

```
18+ Sources
    ↓
Event Hubs + Batch Jobs
    ↓
Bronze Layer (Raw, 213+ tables)
    ↓
Silver Layer (Cleaned, Standardized)
    ↓
Gold Layer (Features, 100+)
    ↓
Feature Store (Time-indexed, commodity-aligned)
    ↓
LightGBM Models (50+ regressors)
    ↓
Orchestration Engine (thresholds, risk filters)
    ↓
Signal Book (PostgreSQL, top 20 ranked)
    ↓
REST API → React Dashboard (6 panels)
    ↓
Trader Signals (Buy/Sell with confidence)
```

---

## Data Freshness & Latency SLAs

| Data Source | Update Frequency | Latency Target | Dashboard Refresh |
|---|---|---|---|
| NYMEX Futures | Every second | <1 second | Real-time |
| EIA Reports | Weekly (Wed 10:30 AM) | Same day | Daily |
| Kpler Tanker Data | Daily (4:05 AM ET) | <1 hour | Daily |
| Genscape Refinery Ops | Real-time | <5 minutes | Real-time |
| Internal Forecasts | Daily | <1 hour | Daily |
| Platts/Argus Prices | Daily | <2 hours | Daily |
| Feature Store | Daily batch | <1 hour after source | Daily |
| Model Inference | Daily batch + ad-hoc | <5 minutes | Real-time on demand |

---

## Database Schema Structure

### Core Tables (Bronze/Silver/Gold)
- Time-series fact tables (prices, volumes, costs)
- Dimension tables (commodities, contracts, locations, suppliers)
- Aggregate tables (daily/weekly summaries)
- Feature tables (pre-computed features indexed by commodity+time)

### Signal Book (PostgreSQL)
- Current and historical signals
- Predicted entry/exit prices
- Confidence scores
- P&L tracking (actual vs predicted)
- Audit trail and lineage

### Cache Layer (Redis)
- Latest signals
- Hot features (frequently queried)
- Model predictions cache
- Dashboard data snapshots

---

## Data Quality Assurance

### Validation Rules
- Schema conformance (correct data types, nullability)
- Range checks (prices > 0, volumes logical)
- Freshness checks (data not stale)
- Duplicate detection (no repeated records)
- Cross-source consistency (no major divergences)

### Monitoring
- Data quality metrics dashboard
- Drift detection (feature value distributions)
- Missing data alerts
- Outlier flagging (statistical anomalies)

### SLA Monitoring
- Ingestion latency tracking
- Source availability monitoring
- Completeness by source
- Accuracy validation via backtesting

---

## Version History

| Date | Change | Impact |
|------|--------|--------|
| 2026-08-09 | Sanitized data model; removed all PII and company-specific references | Public repository safe |
| Earlier | Created comprehensive 18+ source data inventory with 213+ tables | Project foundation |

---

## Related Documentation

- [ROLES_REFERENCE.md](ROLES_REFERENCE.md) — Team roles and system ownership
- [PRODUCTION_ARCHITECTURE.md](PRODUCTION_ARCHITECTURE.md) — Complete system design
- [KNOWLEDGE_GRAPH.html](KNOWLEDGE_GRAPH.html) — Interactive data flow visualization
- Market_Sensing.md — Original business case (10 slides)

---

## Notes

This document represents the complete data model used for the MarketSensing trading signal platform. It is derived from source documentation that contained extensive project implementation details, team assignments, and internal system references. For production deployment, refer to the specific role owners documented in ROLES_REFERENCE.md.
