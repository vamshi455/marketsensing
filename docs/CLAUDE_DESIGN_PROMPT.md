# MarketSensing: Claude Design Prompt

Use this prompt with Claude Design to visualize the MarketSensing platform architecture and data flow.

---

## System Overview

**MarketSensing** is a US oil & gas trading signal platform for a petroleum trading organization. It generates actionable Buy/Sell signals across three arbitrage dimensions:

1. **Time Arbitrage** — Futures curve shape (contango/backwardation)
2. **Location Arbitrage** — Price differences between US physical hubs (Midland, Cushing, Houston)
3. **Crack Spread Arbitrage** — Refining margins (RBOB, ULSD hedging)

**Signal-only in v1** (no direct execution). Designed for future order-management layer.

---

## Data Flow: Left to Right

### 📊 DATA SOURCES (18+)

**Trading Data:**
- NYMEX (WTI, RBOB, ULSD futures) — every second
- Platts/Argus (physical hub prices) — daily
- CFTC (positioning reports) — weekly

**Physical Flows:**
- Kpler (tanker tracking) — daily updates
- Genscape (refinery operations) — real-time

**Inventory & Supply:**
- EIA (weekly inventory, production, refinery runs) — Wednesday 10:30am
- Enverus (upstream rig counts) — weekly
- Maintenance Schedule DB (refinery turnarounds) — weeks ahead

**Internal Operations (Competitive Advantage):**
- MPR/MIPS (production forecasts & sales predictions) — daily
- EIS (customer demand forecasts) — daily/weekly
- TRR (transportation costs) — daily
- TMR (deal tracking & execution history) — real-time
- RDW (risk positions & P&L) — real-time

**Market Intelligence:**
- WoodMac (long-term forecasts) — weekly/monthly
- IIR (market news & sentiment) — daily
- Weather Source (temperature, precipitation) — real-time

---

### 🧠 ML MODELS (LightGBM Regression)

**50+ Models Total** (7 leap durations × 12 commodities, phased rollout in v1)

**Model Types:**

1. **Time Spread Model** (63% precision)
   - Predicts: Front-month vs 3/6/12-month prices
   - Uses: NYMEX, EIA, Weather
   - Output: Buy/Sell contango/backwardation signals

2. **Geographic Arbitrage Model** (58% precision)
   - Predicts: Midland vs Cushing vs Houston spreads
   - Uses: Kpler, Argus, TRR
   - Output: Which hub to buy/sell

3. **Supply Shock Model** (71% precision)
   - Predicts: Supply tightening 1-3 weeks ahead
   - Uses: Genscape, Enverus, Planning DB, EIA
   - Output: Early supply signals

4. **Demand Model** (65% precision)
   - Predicts: Demand surge/decline
   - Uses: Weather, EIS, EIA
   - Output: Demand signals

5. **Risk Filter Model** (99.9% — hard stops)
   - Checks: Position size, correlations, max drawdown
   - Uses: RDW, Internal Risk Limits
   - Output: Approved signals only

6. **Orchestration Engine**
   - Merges 50+ model predictions
   - Ranks by confidence & expected P&L
   - Output: Top 20 ranked trade ideas (Signal Book)
   - Overall: Sharpe ratio 1.94x, 63% directional precision

---

### 📈 TRADER SIGNALS (What Traders See)

**Signal Book** — Top 20 ranked trades per day:

| Field | Example |
|-------|---------|
| Signal ID | UUID + timestamp |
| Trade Idea | "Buy WTI Midland vs Cushing" |
| Entry Price | $82.50/bbl (buy TODAY) |
| Exit Price | $85.20/bbl (sell in 3 days) |
| Expected P&L | $210K average per trade |
| Confidence | 63% probability correct |
| Hold Time | 1-90 days |
| Rationale | "Spread at -2.1 sigma below 60d mean" |

**Dashboard** — 6-panel React interface:
1. **Signals Overview** — Commodity list with BUY/SELL/NEUTRAL
2. **Spread View** — Historical vs forecasted spreads
3. **Market Signal Details** — Entry/exit dates, bid-ask impact
4. **Forecast Distribution** — Confidence intervals
5. **Feature Impact** — Waterfall of top contributing features
6. **P&L Attribution** — Monthly MtM by product/strategy

---

## Technical Architecture

### Data Pipeline
```
18+ Sources 
    ↓ (Azure Event Hubs + ADF)
Delta Lake (Medallion: Bronze/Silver/Gold) — 213+ tables
    ↓
Databricks Feature Store — 100+ pre-computed features
    ↓
LightGBM (50+ models) — Regression predictions
    ↓
Signal Orchestration Engine + Risk Filters
    ↓
PostgreSQL (Signal Book) + Redis (Cache)
    ↓
FastAPI Backend (9+ endpoints)
    ↓
React Dashboard (6-panel, WebSocket real-time)
```

### Infrastructure
- **Compute**: Databricks / Spark (PySpark)
- **Storage**: Delta Lake + Snowflake
- **ML Lifecycle**: MLflow
- **API**: FastAPI (Python 3.11+)
- **Frontend**: React.js / Next.js (TypeScript)
- **Database**: PostgreSQL + Redis
- **Orchestration**: Databricks Workflows / Airflow
- **Deployment**: Kubernetes (AKS) / Docker
- **Monitoring**: Prometheus, Grafana, Jaeger

---

## Performance Targets

| Metric | Target | Current |
|--------|--------|---------|
| Uptime | 99.5% (trading hours) | Design phase |
| API Latency (p95) | <500ms | Design phase |
| Feature Freshness | <1 hour | Design phase |
| Signal Precision | ≥63% | $13.4M historical P&L |
| Sharpe Ratio | ≥1.5 | 1.94x historical |
| Deployment Time | <5 min | Design phase |

---

## Business Impact

- **Historical P&L**: $13.4M over backtest period
- **Directional Precision**: 63% (vs ~50% random)
- **Average Trade**: $210K expected P&L
- **Time to Signal**: <10 seconds (futures), <5 min (physical)
- **Competitive Edge**: Internal ops data (MPR, EIS, TRR, Planning DB) unavailable to competitors

---

## Instruments (v1)

**Futures:**
- WTI (front-month, 3/6/12-month) — NYMEX
- RBOB gasoline (front-month) — NYMEX
- ULSD diesel (front-month) — NYMEX

**Physical Assessments:**
- WTI Midland, WTI Cushing, WTI Houston — Platts/Argus

---

## Implementation Timeline

**Phase 1 (12 weeks)**: WTI spreads + simple rules + basic dashboard
**Phase 2 (6 weeks)**: Crack spreads + regime detection + full monitoring
**Phase 3 (12 weeks)**: Natural gas expansion + execution layer integration

---

## Use This Prompt For:

✅ Create an interactive system architecture diagram  
✅ Show data flow visualization (left→right: sources → models → signals)  
✅ Design the 6-panel React dashboard layout  
✅ Map data dependencies (which source feeds which model)  
✅ Create deployment architecture diagram  
✅ Design database schema visual  
✅ Create feature engineering pipeline diagram  
✅ Show business metrics dashboard mockup  

---

## Key Terminology

| Term | Meaning |
|------|---------|
| **Contango** | Near-term futures cheaper than far-term (normal market) |
| **Backwardation** | Near-term futures more expensive than far-term (tight supply) |
| **Basis** | Price difference between futures and physical |
| **Crack Spread** | RBOB + ULSD value vs WTI (refinery margin) |
| **Z-Score** | How many standard deviations from mean (>2 = opportunity) |
| **Arbitrage** | Profiting from price differences without directional risk |
| **Signal Precision** | % of BUY/SELL signals that were correct predictions |
| **Sharpe Ratio** | Risk-adjusted returns (higher = better, 1.5+ is good) |
| **MtM** | Mark-to-Market (daily P&L update) |

