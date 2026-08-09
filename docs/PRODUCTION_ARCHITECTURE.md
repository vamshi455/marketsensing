# MarketSensing — Production Architecture

**Version**: 1.0 | **Status**: Active | **Target**: Enterprise Deployment
**Last Updated**: 2026-08-09

---

## Executive Summary

Production-grade ML-driven trading signals platform for a US petroleum trading organization. Ingests data from 18+ sources (213+ tables), generates LightGBM-based predictions for 12 commodities across 1-90+ day horizons, and delivers signals via a React.js dashboard for real-time decision-making.

**Core Metrics**:
- **Historical P&L**: $13.4MM realized profits (63% directional precision)
- **Coverage**: 12 commodities × multiple contracts × time horizons
- **Latency**: Real-time feature scoring (sub-minute for futures, 1-5min for physical)
- **Uptime SLA**: 99.5% availability during trading hours

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          DATA INGESTION LAYER                              │
│  ┌──────────┬──────────┬─────────┬──────────┬──────────┬──────────────────┐ │
│  │ ENVERUS  │ WOODMAC  │ WEATHER │ PLANNING │ EIA      │ Other Sources    │ │
│  │ GENSCAPE │ KPLER    │ ECON    │ IIR      │ MPR/MIPS │ (11+ more)       │ │
│  └──────────┴──────────┴─────────┴──────────┴──────────┴──────────────────┘ │
│                    (Event Hubs / Scheduled Jobs)                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                     DATA MEDALLION (Delta Lake)                             │
│  ┌─────────────────────┬────────────────────┬──────────────────────────────┐ │
│  │     BRONZE          │     SILVER         │          GOLD                │ │
│  │  (Raw Events)       │  (Cleaned/STD)     │  (Features/Aggregates)       │ │
│  │                     │                    │                              │ │
│  │ • 213+ raw tables   │ • Deduplicated     │ • 100+ feature sets          │ │
│  │ • Partitioned by    │ • Type-casted      │ • Indexed by                 │ │
│  │   ingestion_date    │ • Null-handled     │   commodity+contract+time    │ │
│  │ • Append-only       │ • Standardized     │ • Optimized for scoring      │ │
│  │                     │   naming           │                              │ │
│  └─────────────────────┴────────────────────┴──────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                    FEATURE ENGINEERING PIPELINE                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │ Feature Store (Databricks FS)                                        │   │
│  │ • Time series resampling (1h, 1d, 1w)                               │   │
│  │ • Spread calculations (time + geo)                                  │   │
│  │ • Technical indicators (MA, RSI, Vol, Z-score)                      │   │
│  │ • Fundamental features (supply, demand, inventory, costs, macro)    │   │
│  │ • Weather impact features                                            │   │
│  │ • 50 leap duration models (1d, 3d, 7d, 14d, 30d, 60d, 90d)         │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ML PIPELINE (LightGBM Models)                            │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │ Model Registry (MLflow)                                              │   │
│  │ • 50+ LightGBM regressors (per leap duration per commodity)          │   │
│  │ • Target: spread values at future anchor dates                       │   │
│  │ • Input: fundamentals + historical data                             │   │
│  │ • Output: regression predictions → thresholds → signals              │   │
│  │ • Backtesting: Precision (63%), Recall, F1-score, R², MAE, RMSE     │   │
│  │ • Retraining: Weekly, triggered on data drift                        │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                      SIGNAL ORCHESTRATION ENGINE                            │
│  • Load latest model predictions                                            │
│  • Merge signals across leap durations                                      │
│  • Apply thresholds → BUY/SELL/NEUTRAL classification                       │
│  • Risk filters (position limits, kill-switches, correlation checks)        │
│  • Conflict resolution (opposing signals from different models)             │
│  • Portfolio-level constraints                                              │
│  • Confidence scoring                                                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌──────────────────────────────────────────────────────────────────────────────┐
│              SIGNAL & EXECUTION LAYER (PostgreSQL)                          │
│  • Signal Book (latest ranked signals)                                      │
│  • P&L Attribution (by deal, product, strategy)                            │
│  • Backtesting results                                                      │
│  • Model performance metrics                                                │
│  • Audit logs & lineage                                                     │
└──────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌──────────────────────────────────────────────────────────────────────────────┐
│                    REACT.JS DASHBOARD (6 Panels)                            │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │ Panel 1: Signals Overview    │  Panel 2: Spread View                  │ │
│  │ • Commodity list             │  • Historical vs forecasted spreads     │ │
│  │ • Contract → Buy/Sell/Neutral │  • Multi-contract series               │ │
│  │ • Model run date filters     │  • Interactive date picker             │ │
│  ├────────────────────────────────────────────────────────────────────────┤ │
│  │ Panel 3: Market Signal Details │  Panel 4: Forecast Distribution      │ │
│  │ • Entry/exit dates           │  • Confidence interval selector        │ │
│  │ • Settlement & entry prices  │  • Buy/Sell distribution visualization│ │
│  │ • Predicted margins          │  • Risk quantification                 │ │
│  ├────────────────────────────────────────────────────────────────────────┤ │
│  │ Panel 5: Feature Impact      │  Panel 6: P&L Attribution              │ │
│  │ • Waterfall chart            │  • Monthly MtM by product              │ │
│  │ • Top N feature contribution │  • Cumulative P&L                      │ │
│  │ • Feature importance ranking │  • Strategy breakdown                  │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  • Real-time filters: Commodity, Spread, Model Run Date, Contract           │
│  • Interactive drill-down from summary to detail                            │
│  • Export to CSV/JSON                                                       │
│  • Mobile responsive                                                        │
└──────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌──────────────────────────────────────────────────────────────────────────────┐
│                    REST API GATEWAY (FastAPI)                               │
│  • /api/signals/latest                                                      │
│  • /api/signals/{strategy_id}                                               │
│  • /api/signals/commodity/{commodity_id}                                    │
│  • /api/spreads/{commodity}/{contract}                                      │
│  • /api/forecasts/{commodity}                                               │
│  • /api/features/{commodity}/{contract}                                     │
│  • /api/pnl/attribution                                                     │
│  • /api/models/performance                                                  │
│  • /api/backtesting/results                                                 │
│  • WebSocket: /ws/signals (real-time signal stream)                         │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Data Source Inventory (18+ Sources)

### Primary Trading Data
1. **NYMEX (Futures)** — WTI, RBOB, ULSD contracts (via TickerTech)
2. **Physical Assessments** — Midland, Cushing, Houston via Platts/Argus (via OPIS)
3. **Kpler** — Real-time product flows, tanker tracking

### Operational Intelligence
4. **EIA** — Weekly/daily inventory, production, refinery runs
5. **Planning DB** — Refinery schedules, turnarounds, capacity planning
6. **Internal Production Forecasts** — Organization internal production/sales forecasts
7. **TRR** — Transportation rates (barge, pipeline, vessel)

### Derivative & Reference Data
8. **ECON** — Macroeconomic data (CPI, S&P500, FX, rates)
9. **WOODMAC** — Long-term commodity forecasts
10. **ENVERUS** — Upstream supply data (production, wells)
11. **Weather Source** — Temperature, wind, precipitation by region

### Enterprise Systems
12. **EIS** (Executive Info System) — Sales forecasts, customer rollups
13. **TMR** (Trading Management) — Deal tracking, costs, margins
14. **IIR** — Market intelligence data
15. **RDW** (Risk Data Warehouse) — P&L attribution, positions, risk exposure
16. **CDM** — Cost data, procurement
17. **KITTYHAWK / RIGHTANGLE** — Optimization models, scenario analysis
18. **CFTC** — Commitment of Traders data

### Data Volumes
- **Total Tables**: 213+
- **Daily Ingestion**: ~2TB across all sources
- **Feature Store**: ~100+ pre-computed feature sets
- **Historical Depth**: 5+ years (for ML training)

---

## Module Architecture

### 1. **Ingestion Layer** (`src/ingestion/`)

```
src/ingestion/
├── connectors/
│   ├── kpler_connector.py           # Real-time product flow API
│   ├── eia_connector.py             # Weekly/daily API pulls
│   ├── weather_connector.py         # Weather Source API
│   ├── database_connector.py        # Direct DB replicas (EIS, TMR, etc.)
│   ├── tickertech_connector.py      # NYMEX futures tick data
│   └── opis_connector.py            # Physical hub assessments
├── streaming/
│   ├── event_hub_consumer.py        # Azure Event Hubs listener
│   ├── kafka_consumer.py            # Kafka fallback
│   └── stream_processors.py         # Windowing, deduplication, enrichment
├── batch/
│   ├── scheduled_jobs.py            # Daily/weekly ingestion schedules
│   ├── data_factory_orchestrator.py # Trigger ADF pipelines
│   └── backfill_manager.py          # Historical data loading
├── validation/
│   ├── schema_validator.py          # Avro/JSON schema validation
│   ├── quality_checks.py            # Freshness, nullability, ranges
│   └── anomaly_detector.py          # Statistical drift detection
└── __init__.py
```

**Key Points**:
- Separate connectors for each source (maintainability, testability)
- Streaming for tick data (futures), scheduled batch for reference data
- Schema validation at ingestion boundary (fail-fast)
- Quality scoring per record (used in feature engineering)

---

### 2. **Feature Engineering** (`src/features/`)

```
src/features/
├── time_series/
│   ├── resampler.py                 # OHLCV bars (1h, 1d, 1w)
│   ├── alignment.py                 # Align multi-source data
│   └── gaps.py                      # Handle missing data
├── spreads/
│   ├── time_spreads.py              # F1 vs F3, F1 vs F6, etc.
│   ├── geo_spreads.py               # Midland vs Cushing, etc.
│   ├── crack_spreads.py             # 3:2:1 RBOB/ULSD vs crude
│   └── basis_calc.py                # Physical-to-futures basis
├── technical/
│   ├── indicators.py                # MA, RSI, Bollinger Bands, Z-score
│   ├── volatility.py                # Rolling vol, GARCH
│   └── momentum.py                  # Rate of change, MACD
├── fundamentals/
│   ├── supply_features.py           # Refinery runs, production, exports
│   ├── demand_features.py           # Sales, consumption by segment
│   ├── inventory_features.py        # Levels, changes, seasonal norms
│   ├── costs_features.py            # Refining, transport, storage
│   ├── macro_features.py            # CPI, employment, FX, rates
│   └── weather_features.py          # Temp impact on demand
├── store/
│   ├── feature_store.py             # Databricks FS integration
│   ├── cache_layer.py               # Redis caching for hot features
│   └── batch_producer.py            # Materialize features offline
└── __init__.py
```

**Key Points**:
- 100+ features per commodity × leap duration
- Organized by category (time series, spreads, technicals, fundamentals)
- Feature store as single source of truth for model training & scoring
- Automated drift detection (compare current vs historical distributions)

---

### 3. **ML Pipeline** (`src/ml/`)

```
src/ml/
├── models/
│   ├── lgb_trainer.py               # LightGBM training loop
│   ├── hyperparameter_tuning.py     # Optuna-based HPO
│   ├── feature_selection.py         # Auto feature importance ranking
│   └── ensemble.py                  # Combine models across leap durations
├── data_prep/
│   ├── target_constructor.py        # Spread values at anchor dates
│   ├── train_test_split.py          # Temporal (walk-forward) split
│   ├── scaling.py                   # StandardScaler, RobustScaler
│   └── class_balance.py             # Handle Buy/Sell/Neutral imbalance
├── evaluation/
│   ├── backtester.py                # Historical signal replay
│   ├── metrics.py                   # Precision, Recall, F1, R², MAE, RMSE
│   ├── feature_importance.py        # Waterfall charts, SHAP
│   └── drift_detection.py           # Model performance degradation
├── serving/
│   ├── model_loader.py              # MLflow model registry
│   ├── batch_scoring.py             # Nightly batch predictions
│   ├── online_scoring.py            # Real-time inference endpoint
│   └── prediction_cache.py          # Cache for repeated queries
├── monitoring/
│   ├── performance_tracker.py       # Track live signal performance
│   ├── alert_manager.py             # Flag failing models
│   └── retraining_trigger.py        # Auto-retrain on drift
└── __init__.py
```

**Key Points**:
- 50+ LightGBM models (one per leap duration + commodity combination)
- Walk-forward backtesting (realistic out-of-sample evaluation)
- Automatic retraining on data drift (weekly or triggered)
- Feature importance tracking (what drives each prediction?)

---

### 4. **Signal Orchestration** (`src/orchestration/`)

```
src/orchestration/
├── signal_generator.py              # Predictions → thresholds → signals
├── signal_merger.py                 # Combine multi-leap signals
├── risk_filters.py                  # Position limits, correlations
├── conflict_resolver.py             # Opposing signals resolution
├── portfolio_optimizer.py           # Portfolio-level constraints
├── confidence_scorer.py             # Model agreement, prediction magnitude
└── __init__.py
```

**Logic**:
1. Load latest LightGBM predictions for all commodities × leap durations
2. Apply signal thresholds (e.g., prediction > 75th percentile = BUY)
3. Merge across leap durations (e.g., all time horizons signal BUY → high confidence)
4. Risk filters (e.g., don't exceed 50 contracts per commodity)
5. Conflict resolution (if spread predictions diverge, take majority vote)
6. Rank by confidence & expected P&L
7. Store to Signal Book

---

### 5. **API Gateway** (`src/api/`)

```
src/api/
├── main.py                          # FastAPI app
├── auth/
│   ├── oauth.py                     # AD/LDAP integration
│   └── rbac.py                      # Role-based access control
├── routes/
│   ├── signals.py                   # GET /signals/*, /signal-book
│   ├── spreads.py                   # GET /spreads/{commodity}
│   ├── forecasts.py                 # GET /forecasts/{commodity}
│   ├── features.py                  # GET /features/{commodity}/{contract}
│   ├── models.py                    # GET /models/performance
│   ├── pnl.py                       # GET /pnl/attribution
│   ├── backtesting.py               # GET /backtesting/results
│   ├── health.py                    # GET /health
│   └── websocket.py                 # WS /ws/signals (real-time)
├── schemas/
│   ├── signal_schema.py             # Pydantic models
│   ├── spread_schema.py
│   └── pnl_schema.py
├── middleware/
│   ├── logging.py                   # Structured logging
│   ├── error_handling.py            # Global error handler
│   └── rate_limiting.py             # API throttling
└── __init__.py
```

**Endpoints**:
- `GET /signals/latest` — Latest signals across all commodities
- `GET /signals/{strategy_id}` — Signals for specific strategy
- `GET /signals/commodity/{commodity_id}` — Signals for commodity
- `GET /signal-book` — Ranked trade ideas
- `GET /spreads/{commodity}/{contract}` — Historical + forecasted spreads
- `GET /forecasts/{commodity}` — Regression predictions
- `GET /features/{commodity}/{contract}` — Feature values used in prediction
- `GET /models/performance` — Model backtesting metrics
- `GET /pnl/attribution` — Monthly P&L by product/strategy
- `WS /ws/signals` — Real-time signal stream

---

### 6. **Persistence Layer** (`src/persistence/`)

```
src/persistence/
├── bronze_layer.py                  # Raw events (Delta Lake)
├── silver_layer.py                  # Cleaned data (Delta Lake)
├── gold_layer.py                    # Features (Delta Lake)
├── signal_db.py                     # PostgreSQL signal book
├── pnl_db.py                        # PostgreSQL P&L tracking
├── cache.py                         # Redis for hot data
├── schema_registry.py               # Avro schema management
└── __init__.py
```

**Storage Strategy**:
- **Delta Lake** (medallion): Bronze/Silver/Gold for data lineage & audit
- **PostgreSQL**: Signal Book, P&L Attribution (low-latency queries)
- **Redis**: Hot signals, feature cache (sub-millisecond reads)
- **Snowflake**: Analytics/reporting sync (nightly batch)

---

### 7. **React.js Frontend** (`web/`)

```
web/
├── public/
├── src/
│   ├── components/
│   │   ├── SignalsOverview.tsx       # Panel 1
│   │   ├── SpreadView.tsx            # Panel 2
│   │   ├── MarketSignalDetails.tsx   # Panel 3
│   │   ├── ForecastDistribution.tsx  # Panel 4
│   │   ├── FeatureImpact.tsx         # Panel 5
│   │   ├── PnLAttribution.tsx        # Panel 6
│   │   ├── Filters.tsx               # Commodity, Spread, Date filters
│   │   ├── Navigation.tsx            # Sidebar (Signal Summary, Backtesting)
│   │   └── shared/
│   │       ├── Table.tsx
│   │       ├── Chart.tsx
│   │       ├── Tooltip.tsx
│   │       └── Modal.tsx
│   ├── services/
│   │   ├── api.ts                    # API client (axios)
│   │   ├── websocket.ts              # WebSocket for real-time updates
│   │   └── cache.ts                  # Client-side caching
│   ├── hooks/
│   │   ├── useSignals.ts
│   │   ├── useSpreads.ts
│   │   ├── useFilters.ts
│   │   └── useWebSocket.ts
│   ├── types/
│   │   ├── signal.ts
│   │   ├── spread.ts
│   │   ├── pnl.ts
│   │   └── common.ts
│   ├── pages/
│   │   ├── Dashboard.tsx             # Main 6-panel layout
│   │   ├── Backtesting.tsx           # Backtesting results
│   │   ├── ModelPerformance.tsx      # Model metrics
│   │   └── Settings.tsx              # Config management
│   ├── styles/
│   │   ├── theme.ts                  # Dark/light theme
│   │   ├── global.css
│   │   └── components.css
│   ├── utils/
│   │   ├── formatting.ts             # Number/date formatting
│   │   ├── colors.ts                 # Color scales for signals
│   │   └── validators.ts
│   ├── App.tsx
│   └── index.tsx
├── package.json
└── tsconfig.json
```

**Technology Stack**:
- **React 18** + TypeScript
- **Next.js** (if SSR needed)
- **Recharts** (charts & visualizations)
- **TanStack Table** (data tables)
- **Tailwind CSS** (styling)
- **React Query** (server state)
- **Redux** (client state, if complex)
- **WebSocket** (real-time signal updates)

---

### 8. **Monitoring & Observability** (`src/monitoring/`)

```
src/monitoring/
├── logging.py                       # Structured logging (JSON)
├── metrics.py                       # Prometheus metrics
├── tracing.py                       # Distributed tracing (Jaeger)
├── alerting.py                      # PagerDuty/Slack integration
└── dashboards/
    ├── data_freshness.py            # Monitor data pipeline delays
    ├── model_performance.py         # Track signal precision/recall
    ├── api_metrics.py               # Latency, throughput, errors
    └── business_metrics.py          # P&L, signal count, etc.
```

**Key Metrics**:
- Data freshness (age of latest NYMEX tick, EIA report)
- Model performance (precision, recall, F1 on holdout)
- API latency (p50, p95, p99)
- Signal generation latency
- P&L per commodity & strategy
- Alert: Model prediction drift, missing data, API errors

---

## Data Flow Sequence

### Real-time (Futures Signals)

```
1. NYMEX tick → Event Hubs
2. Stream processor → dedup, enrich (1-5 sec)
3. Feature store: update rolling bars, spreads
4. LightGBM scorer: 50 models in parallel (~500ms)
5. Orchestrator: merge results, apply thresholds (100ms)
6. Signal Book update (PostgreSQL)
7. WebSocket broadcast to dashboard (real-time)
8. API /signals/latest response
```

**Total latency**: 2-10 seconds from NYMEX tick to Signal Book

### Batch (Daily Features & Retraining)

```
1. 6am UTC: EIA, weather, fundamental data pulled
2. Data → Bronze layer (Delta Lake)
3. Silver layer: cleansing, deduplication (10 min)
4. Gold layer: feature engineering (20 min)
5. Feature store materialization (5 min)
6. Weekly: LightGBM retraining on latest data (2 hours)
7. MLflow model registry update
8. Batch scoring for all commodities/leap durations (30 min)
9. Signal Book rebuilt from fresh predictions
```

**Total duration**: ~3 hours for full daily cycle

---

## Deployment & Infrastructure

### Cloud: Azure (Standard Cloud Infrastructure)

```
Azure Data Factory       Azure Databricks        Azure SQL Server
├─ Orchestration        ├─ PySpark jobs         ├─ Signal Book
├─ Scheduled jobs       ├─ Feature store        ├─ P&L attribution
└─ Data movement        ├─ ML pipeline          └─ Audit logs
                        └─ Monitoring           
                                               
Azure Event Hubs        PostgreSQL              Azure Cosmos DB
├─ Streaming ingestion  ├─ Real-time cache      ├─ Session data
└─ Tick data           └─ Analytics            └─ User preferences

Azure App Service / AKS
├─ FastAPI server (API gateway)
└─ React frontend (CDN)
```

### Containerization

```dockerfile
# API service
FROM python:3.11-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ /app/src/
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```dockerfile
# Feature engineering job (Databricks)
FROM databricks/spark-py:3.3.2
COPY src/features /app/features/
```

### Kubernetes Manifest (AKS)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: marketsensing-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: marketsensing-api
  template:
    metadata:
      labels:
        app: marketsensing-api
    spec:
      containers:
      - name: api
        image: myregistry.azurecr.io/marketsensing-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secrets
              key: connection-string
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
      - name: prometheus-exporter
        image: myregistry.azurecr.io/prometheus-exporter:latest
```

---

## Security & Compliance

### Authentication & Authorization
- **LDAP/OAuth** for user identity and access control
- **OAuth 2.0** for API access (service accounts)
- **RBAC**: Trader, Analyst, Administrator roles
- **API key rotation**: Quarterly
- **Secret rotation**: Automated via Azure Key Vault

### Data Security
- **Encryption at rest**: AES-256 (Delta Lake, PostgreSQL)
- **Encryption in transit**: TLS 1.3
- **PII masking**: User names, trading desk identities in logs
- **Audit trails**: All signal generation & P&L changes logged

### Compliance
- **SOX**: Financial controls on signal generation
- **GDPR/CCPA**: Data retention policies (5-year archival)
- **Export control**: No data to sanctioned countries
- **Model governance**: Model cards, training data provenance

---

## Performance & SLAs

| Metric | Target | Monitoring |
|--------|--------|------------|
| **Uptime (trading hours)** | 99.5% | CloudWatch alarms |
| **Signal latency (futures)** | <10 sec | Prometheus histograms |
| **Signal latency (physical)** | <5 min | Databricks job timers |
| **API p95 latency** | <500ms | API middleware |
| **Feature store freshness** | <1 hour | Data validation jobs |
| **Model retraining cadence** | Weekly | MLflow scheduled runs |
| **Dashboard load time** | <2 sec | Synthetic monitoring |

---

## Development Roadmap

### Phase 1 (Months 1-3): Production Core
- ✅ Ingest 18+ data sources (213+ tables)
- ✅ Build medallion architecture (Bronze/Silver/Gold)
- ✅ Feature engineering pipeline (100+ features)
- ✅ LightGBM training & inference
- ✅ Signal orchestration engine
- ✅ PostgreSQL persistence
- ✅ FastAPI gateway

### Phase 2 (Months 4-6): React Frontend & Optimization
- ✅ React.js 6-panel dashboard
- ✅ Real-time WebSocket updates
- ✅ Performance optimization (caching, indexing)
- ✅ Advanced analytics (drill-down, drill-through)
- ✅ Mobile responsive design

### Phase 3 (Months 7-9): ML Enhancements & Automation
- ✅ Regime detection (HMM/clustering)
- ✅ Hyperparameter auto-tuning (Optuna)
- ✅ Feature drift monitoring
- ✅ Automated retraining on drift
- ✅ Ensemble methods (stacking)

### Phase 4 (Month 10+): Execution & Scale
- ✅ Integration with OMS (order management)
- ✅ Auto-execution on qualified signals
- ✅ Natural gas & new products
- ✅ Advanced visualization (3D term structures)
- ✅ Multi-desk federation

---

## References

- `docs/Market_Sensing.md` — Business presentation (13.4MM P&L, metrics)
- `docs/Market_Sensing_Sources.xlsx` — Full source & table inventory
- `CLAUDE.md` — Project memory & conventions
- `config/` — Strategy parameters, risk limits, schedules
