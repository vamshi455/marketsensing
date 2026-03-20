# MarketSensing - Oil & Gas Trading Signal Platform

## Project Overview

A **market-sensing and trading-signal platform** for a US-focused oil & gas trading organization. The system generates actionable **Buy/Sell signals** across three arbitrage dimensions:

- **Time arbitrage** — futures curve shape (contango/backwardation)
- **Location arbitrage** — price differences between US physical hubs
- **Refining margin (crack) arbitrage** — hedging and optimizing refinery margins

Signal-only in v1 (no direct execution). Designed for a future order-management/execution layer.

---

## Architecture Overview

```mermaid
graph TB
    subgraph "Data Sources"
        MKT[Market Data<br/>NYMEX WTI/RBOB/ULSD]
        FUND[Fundamentals<br/>EIA/Baker Hughes]
        PHYS[Physical Prices<br/>Midland/Cushing/MEH]
        CAL[Event Calendar<br/>EIA/FOMC/Weather]
    end

    subgraph "Ingestion Layer"
        STREAM[Streaming Ingestion<br/>Event Hubs / Kafka]
        BATCH[Batch Ingestion<br/>ADF / Scheduled Jobs]
        SCHEMA[Schema Registry<br/>& Validation]
    end

    subgraph "Storage (Medallion)"
        BRONZE[Bronze<br/>Raw Events]
        SILVER[Silver<br/>Cleaned & Conformed]
        GOLD[Gold<br/>Features & Aggregates]
    end

    subgraph "Feature Engineering"
        PRICE[Price Series<br/>Resampled Bars]
        SPREAD[Spread Calculator<br/>Location/Time/Crack]
        TECH[Technical Indicators<br/>MA/RSI/Vol/Z-Score]
        FUNDA[Fundamental Features<br/>Inventory Surprise/Seasonal]
        FS[Feature Store<br/>Time+Instrument Indexed]
    end

    subgraph "Signal Models"
        RULE[Rules-Based Signals<br/>Z-Score Thresholds]
        ML[ML Signals<br/>Mean-Reversion/Regime]
        RISK[Risk Filters<br/>Limits/Kill-Switches]
    end

    subgraph "Decision & Output"
        ORCH[Orchestrator<br/>Priority & Conflict Resolution]
        BOOK[Signal Book<br/>Ranked Trade Ideas]
        API[REST API<br/>Signal Output]
        DASH[Dashboards<br/>Snowflake + BI]
    end

    subgraph "Monitoring"
        BT[Backtesting Engine]
        PNL[P&L Attribution]
        KPI[Signal Health KPIs]
    end

    MKT --> STREAM
    PHYS --> STREAM
    FUND --> BATCH
    CAL --> BATCH
    STREAM --> SCHEMA --> BRONZE
    BATCH --> SCHEMA
    BRONZE --> SILVER --> GOLD
    GOLD --> PRICE & SPREAD & TECH & FUNDA
    PRICE & SPREAD & TECH & FUNDA --> FS
    FS --> RULE & ML
    RULE & ML --> RISK --> ORCH
    ORCH --> BOOK --> API & DASH
    BOOK --> BT & PNL & KPI
```

---

## Trading Concepts → System Components Mapping

| Trading Concept | System Module | Key Features |
|---|---|---|
| Buy Low, Sell High (directional) | Signal Models → Rules + ML | Z-scores, RSI, mean-reversion models |
| Spread Arbitrage (relative value) | Feature Engineering → Spread Calculator | Location spreads, crack spreads |
| Time Arbitrage (term structure) | Feature Engineering → Price Series + Signal Models | Contango/backwardation detection, storage economics |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Streaming Ingestion | Azure Event Hubs / Kafka |
| Batch Ingestion | Azure Data Factory (ADF) |
| Compute / Pipelines | Databricks / Spark (PySpark) |
| Storage | Delta Lake (medallion) + Snowflake (analytics) |
| ML Lifecycle | MLflow |
| Feature Store | Databricks Feature Store / custom Delta tables |
| API | FastAPI (Python) |
| Dashboards | Power BI / Streamlit |
| Orchestration | Databricks Workflows / Airflow |
| Language | Python 3.11+ |

---

## Project Structure

```
marketsensing/
├── CLAUDE.md                          # Project memory & instructions
├── README.md                          # Quick start guide
├── pyproject.toml                     # Python project config
├── .gitignore                         # Git ignore rules
│
├── docs/                              # Architecture & specs
│   ├── architecture.md                # System architecture overview
│   ├── decisions/                     # Architecture decision records (ADRs)
│   │   ├── 001-medallion-architecture.md
│   │   ├── 002-config-driven-signals.md
│   │   └── 003-signal-only-v1.md
│   ├── runbooks/                      # Operational runbooks
│   │   └── eia-report-day.md
│   ├── schemas/                       # Data schemas (Bronze/Silver/Gold)
│   │   ├── bronze.md
│   │   ├── silver.md
│   │   └── gold.md
│   └── api/                           # API contracts
│       └── signal-api-contract.md
│
├── .claude/                           # Claude Code configuration
│   ├── settings.json                  # Permissions & settings
│   ├── hooks/                         # Automation hooks
│   │   └── pre-commit.sh
│   └── skills/                        # Reusable AI workflows
│       ├── code-review/
│       │   └── SKILL.md
│       ├── refactor/
│       │   └── SKILL.md
│       └── release/
│           └── SKILL.md
│
├── src/                               # Core application modules
│   ├── ingestion/                     # Data ingestion connectors
│   │   ├── streaming/                 # Real-time market data
│   │   └── batch/                     # EIA, rig counts, etc.
│   ├── features/                      # Feature engineering
│   │   ├── prices.py                  # Price resampling
│   │   ├── spreads.py                 # Spread calculations
│   │   ├── technicals.py             # Technical indicators
│   │   └── fundamentals.py           # Fundamental features
│   ├── signals/                       # Signal generation
│   │   ├── rules/                     # Rules-based signals
│   │   ├── ml/                        # ML-based signals
│   │   └── risk/                      # Risk filters & kill-switches
│   ├── orchestration/                 # Signal combination & decision
│   ├── api/                           # REST API for signal output
│   │   └── CLAUDE.md                  # API module context
│   ├── persistence/                   # Delta Lake & Snowflake storage
│   │   └── CLAUDE.md                  # Persistence module context
│   └── monitoring/                    # Backtesting, P&L, KPIs
│
├── config/                            # YAML configuration (never hard-code)
│   ├── instruments.yaml               # Instrument definitions
│   ├── strategies.yaml                # Strategy parameters & thresholds
│   ├── risk_limits.yaml               # Risk limits & kill-switches
│   └── schedules.yaml                 # Event & ingestion schedules
│
├── tools/                             # Development utilities
│   ├── scripts/                       # Helper scripts
│   └── prompts/                       # Prompt templates
│
├── notebooks/                         # Databricks / Jupyter notebooks
├── tests/                             # Unit and integration tests
└── infra/                             # IaC (Terraform/Bicep)
```

---

## Instruments (v1)

| Instrument ID | Description | Source |
|---|---|---|
| `WTI_CL_F1` | WTI front-month future | NYMEX |
| `WTI_CL_F3` | WTI 3-month future | NYMEX |
| `WTI_CL_F6` | WTI 6-month future | NYMEX |
| `WTI_CL_F12` | WTI 12-month future | NYMEX |
| `WTI_MIDLAND` | WTI Midland physical assessment | Platts/Argus |
| `WTI_CUSHING` | WTI Cushing physical assessment | Platts/Argus |
| `WTI_HOUSTON` | WTI Houston (MEH) physical assessment | Platts/Argus |
| `RBOB_F1` | RBOB gasoline front-month | NYMEX |
| `ULSD_F1` | ULSD diesel front-month | NYMEX |

---

## Signal Output Schema

All signals conform to this structure:

```json
{
  "signal_id": "uuid",
  "timestamp": "ISO-8601",
  "strategy_id": "spread_midland_cushing",
  "instrument_long": "WTI_MIDLAND",
  "instrument_short": "WTI_CUSHING",
  "action": "enter | exit",
  "side": "long_spread | short_spread",
  "size": 10,
  "confidence": 0.82,
  "expected_hold_time": "3d",
  "rationale": "Spread at -2.1 sigma below 60d mean",
  "model_version": "v1.2.0",
  "risk_checks_passed": true
}
```

---

## Delivery Phases

### Phase 1 — WTI Spreads + Simple Rules
- Ingest NYMEX WTI futures (EOD + delayed streaming)
- Physical hub prices (Midland, Cushing, Houston)
- Location spread features + z-score signals
- Time spread features + contango/backwardation signals
- Basic Signal Book API
- Backtesting framework

### Phase 2 — Crack Spreads + Regime Detection
- RBOB, ULSD ingestion
- 3-2-1 crack spread features + signals
- HMM / clustering regime detection
- Regime-aware signal gating
- EIA inventory surprise features
- Dashboard + P&L attribution

### Phase 3 — Natural Gas + Expansion
- Henry Hub + gas basis hubs (Waha, Chicago, Algonquin)
- Gas storage signals
- Full monitoring suite
- Execution layer integration design

---

## Conventions

- **Python**: PEP 8, type hints, `ruff` for linting
- **Config**: all thresholds/windows/limits in YAML, never hard-coded
- **Testing**: pytest, minimum 80% coverage for signal logic
- **Branching**: feature branches → `main` via PR
- **Commits**: conventional commits (`feat:`, `fix:`, `docs:`, etc.)
