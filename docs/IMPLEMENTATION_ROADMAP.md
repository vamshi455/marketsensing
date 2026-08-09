# MarketSensing Implementation Roadmap

**Target**: Production deployment with 18+ data sources, ML pipeline, and React dashboard
**Timeline**: 10-12 weeks for Phase 1 (core platform)
**Status**: Initial scaffolding complete, now implementing modules in parallel

---

## Phase 1: Core Platform (Weeks 1-12)

### Sprint 1 (Weeks 1-2): Data Ingestion Foundation

**Objective**: Establish data pipelines from all 18+ sources into Bronze layer

**Tasks**:

1. **Connector Infrastructure** ✅ Started
   - [x] `src/ingestion/base_connector.py` — Abstract base class
   - [ ] `src/ingestion/connectors/kpler_connector.py` — Real-time product flows
   - [ ] `src/ingestion/connectors/tickertech_connector.py` — NYMEX futures
   - [ ] `src/ingestion/connectors/eia_connector.py` — Weekly/daily EIA data
   - [ ] `src/ingestion/connectors/weather_connector.py` — Weather data
   - [ ] `src/ingestion/connectors/database_connector.py` — Direct DB replicas (EIS, TMR, TRR, etc.)
   - [ ] `src/ingestion/connectors/opis_connector.py` — Physical hub assessments

2. **Streaming Ingestion**
   - [ ] `src/ingestion/streaming/event_hub_consumer.py` — Azure Event Hubs listener
   - [ ] `src/ingestion/streaming/stream_processors.py` — Deduplication, enrichment
   - [ ] Test with mock NYMEX tick data

3. **Batch Ingestion**
   - [ ] `src/ingestion/batch/scheduled_jobs.py` — Airflow/ADF orchestration
   - [ ] `config/schedules.yaml` — Update with real schedules (EIA: Wed 10:30am, etc.)

4. **Data Validation**
   - [ ] `src/ingestion/validation/schema_validator.py` — Avro/JSON schema enforcement
   - [ ] `src/ingestion/validation/quality_checks.py` — Freshness, nullability
   - [ ] Schema definitions for each source (YAML)

5. **Deliverables**
   - Raw data flowing into Delta Lake Bronze layer
   - Schema validation passing for all 18 sources
   - Error handling & retry logic for production
   - Monitoring dashboard showing ingestion health

**Success Metrics**:
- All 18 sources connected and validated
- <2% data loss rate
- Sub-minute latency for streaming, daily cadence for batch

---

### Sprint 2 (Weeks 3-4): Feature Engineering

**Objective**: Build Feature Store with 100+ features across all categories

**Tasks**:

1. **Feature Store Setup**
   - [ ] `src/features/store/feature_store.py` — Databricks FS integration
   - [ ] Initialize Databricks Feature Store tables
   - [ ] Design schema for time + commodity + contract indexing

2. **Time Series Features**
   - [ ] `src/features/time_series/resampler.py` — OHLCV bars (1h, 1d, 1w)
   - [ ] `src/features/time_series/alignment.py` — Cross-source alignment
   - [ ] `src/features/time_series/gaps.py` — Missing data handling

3. **Spread Features**
   - [ ] `src/features/spreads/time_spreads.py` — F1-F3, F1-F6, etc.
   - [ ] `src/features/spreads/geo_spreads.py` — Midland-Cushing, etc.
   - [ ] `src/features/spreads/crack_spreads.py` — 3:2:1 RBOB/ULSD
   - [ ] `src/features/spreads/basis_calc.py` — Physical-to-futures basis

4. **Technical Indicators**
   - [ ] `src/features/technical/indicators.py` — MA, RSI, Bollinger Bands, Z-score
   - [ ] `src/features/technical/volatility.py` — Rolling vol, GARCH
   - [ ] `src/features/technical/momentum.py` — ROC, MACD

5. **Fundamental Features**
   - [ ] `src/features/fundamentals/supply_features.py` — Refinery runs, production
   - [ ] `src/features/fundamentals/demand_features.py` — Sales by segment
   - [ ] `src/features/fundamentals/inventory_features.py` — Levels & changes
   - [ ] `src/features/fundamentals/costs_features.py` — Refining, transport, storage
   - [ ] `src/features/fundamentals/macro_features.py` — CPI, employment, FX, rates
   - [ ] `src/features/fundamentals/weather_features.py` — Temp impact on demand

6. **Feature Engineering Pipeline**
   - [ ] `src/features/store/batch_producer.py` — Nightly materialization
   - [ ] Validation: all 100+ features populated
   - [ ] Caching layer: Redis for hot features

7. **Deliverables**
   - Feature Store with 100+ pre-computed features
   - Daily batch updates (6am UTC)
   - Feature drift monitoring
   - Documentation of feature engineering logic

**Success Metrics**:
- All 100+ features populated and validated
- <1 hour for nightly materialization
- No missing values in feature store

---

### Sprint 3 (Weeks 5-6): ML Pipeline

**Objective**: LightGBM training, evaluation, and inference infrastructure

**Tasks**:

1. **Data Preparation**
   - [ ] `src/ml/data_prep/target_constructor.py` — Spread values at anchor dates
   - [ ] `src/ml/data_prep/train_test_split.py` — Walk-forward temporal split
   - [ ] `src/ml/data_prep/scaling.py` — StandardScaler, RobustScaler
   - [ ] Historical data: 5 years of training data

2. **Model Training**
   - [ ] `src/ml/models/lgb_trainer.py` — LightGBM regression (50 models)
   - [ ] Leap durations: 1d, 3d, 7d, 14d, 30d, 60d, 90d (7 models per commodity)
   - [ ] 12 commodities → 84 total models (but start with 3 commodities)

3. **Hyperparameter Tuning**
   - [ ] `src/ml/models/hyperparameter_tuning.py` — Optuna-based HPO
   - [ ] Auto feature selection
   - [ ] Cross-validation on walk-forward splits

4. **Model Evaluation**
   - [ ] `src/ml/evaluation/backtester.py` — Historical signal replay
   - [ ] `src/ml/evaluation/metrics.py` — Precision, Recall, F1, R², MAE, RMSE
   - [ ] `src/ml/evaluation/feature_importance.py` — Waterfall charts, SHAP values
   - [ ] Target: 63% precision (from historical $13.4MM P&L)

5. **Model Registry**
   - [ ] `src/ml/serving/model_loader.py` — MLflow integration
   - [ ] Version control for all models
   - [ ] Model lineage tracking

6. **Batch Scoring**
   - [ ] `src/ml/serving/batch_scoring.py` — Nightly predictions for all commodities
   - [ ] ~30 minutes for 84 models × 12 commodities

7. **Deliverables**
   - 50+ LightGBM models in MLflow
   - Backtesting results showing ≥60% precision
   - Model performance dashboards
   - Weekly retraining pipeline

**Success Metrics**:
- Models achieving ≥60% precision
- Sharpe ratio ≥1.5 (from historical data)
- <30 min for batch scoring
- Feature importance distributions match expectations

---

### Sprint 4 (Weeks 7-8): Signal Orchestration & API

**Objective**: Signal generation engine + FastAPI gateway

**Tasks**:

1. **Signal Generation**
   - [ ] `src/orchestration/signal_generator.py` — Predictions → thresholds → signals
   - [ ] Threshold tuning (e.g., percentile-based)
   - [ ] BUY/SELL/NEUTRAL classification

2. **Signal Merging & Conflict Resolution**
   - [ ] `src/orchestration/signal_merger.py` — Combine multi-leap signals
   - [ ] `src/orchestration/conflict_resolver.py` — Opposing signals logic

3. **Risk Filters**
   - [ ] `src/orchestration/risk_filters.py` — Position limits, correlations
   - [ ] `src/orchestration/portfolio_optimizer.py` — Portfolio-level constraints

4. **Confidence Scoring**
   - [ ] `src/orchestration/confidence_scorer.py` — Model agreement, prediction magnitude

5. **Signal Book**
   - [ ] `src/persistence/signal_db.py` — PostgreSQL schema
   - [ ] Ranking by confidence & expected P&L
   - [ ] Update frequency: real-time for futures, 5min for physical

6. **FastAPI Gateway** ✅ Started
   - [x] `src/api/main.py` — Skeleton
   - [ ] `/signals/latest`, `/signal-book` endpoints
   - [ ] `/spreads/{commodity}/{contract}` endpoint
   - [ ] `/forecasts/{commodity}` endpoint
   - [ ] `/features/{commodity}/{contract}` endpoint
   - [ ] `/models/performance` endpoint
   - [ ] `/pnl/attribution` endpoint
   - [ ] `/backtesting/results` endpoint
   - [ ] WebSocket `/ws/signals` for real-time updates

7. **API Auth & Security**
   - [ ] AD/LDAP integration
   - [ ] OAuth 2.0 for service accounts
   - [ ] RBAC (Trader, Analyst, Admin roles)
   - [ ] API key rotation

8. **Testing**
   - [ ] Unit tests for signal generation logic
   - [ ] Integration tests for end-to-end signal flow
   - [ ] Load tests (1000+ concurrent API requests)

9. **Deliverables**
   - FastAPI server running with all endpoints
   - Signal Book updated in real-time
   - API documented with OpenAPI/Swagger
   - Tests passing with >80% coverage

**Success Metrics**:
- API p95 latency <500ms
- Signal generation latency <10sec
- All endpoints responding with valid data
- Auth/RBAC working correctly

---

### Sprint 5 (Weeks 9-10): React.js Dashboard

**Objective**: Production-grade 6-panel frontend replacing Power BI

**Tasks**:

1. **Project Setup**
   - [x] `web/package.json` with Next.js, Recharts, TanStack
   - [ ] TypeScript configuration
   - [ ] Tailwind CSS setup
   - [ ] ESLint & Prettier

2. **Core Components**
   - [ ] `web/src/pages/Dashboard.tsx` — 6-panel main layout ✅ Started
   - [x] `web/src/components/SignalsOverview.tsx` — Panel 1 ✅ Started
   - [ ] `web/src/components/SpreadView.tsx` — Panel 2
   - [ ] `web/src/components/MarketSignalDetails.tsx` — Panel 3
   - [ ] `web/src/components/ForecastDistribution.tsx` — Panel 4
   - [ ] `web/src/components/FeatureImpact.tsx` — Panel 5
   - [ ] `web/src/components/PnLAttribution.tsx` — Panel 6

3. **Shared Components**
   - [ ] `web/src/components/shared/Table.tsx` — Data table with sorting/filtering
   - [ ] `web/src/components/shared/Chart.tsx` — Recharts wrapper
   - [ ] `web/src/components/shared/Tooltip.tsx` — Custom tooltips
   - [ ] `web/src/components/shared/Modal.tsx` — Modal dialogs

4. **Filter System**
   - [ ] `web/src/components/Filters.tsx` — Commodity, Spread, Date filters
   - [ ] `web/src/components/Navigation.tsx` — Sidebar (Signals, Backtesting)
   - [ ] Filter persistence (URL params or localStorage)

5. **API Integration**
   - [ ] `web/src/services/api.ts` — Axios client with auth
   - [ ] `web/src/hooks/useSignals.ts` — React Query hook
   - [ ] `web/src/hooks/useSpreads.ts` — Spread data fetching
   - [ ] `web/src/hooks/useFilters.ts` — Filter state management

6. **Real-time Updates**
   - [ ] `web/src/services/websocket.ts` — WebSocket connection
   - [ ] Auto-refresh signals (1-minute polling + WebSocket)
   - [ ] Real-time P&L updates

7. **Styling & Theming**
   - [ ] Dark theme (default)
   - [ ] Light theme toggle
   - [ ] Mobile responsive design
   - [ ] Accessibility (WCAG 2.1 AA)

8. **Build & Deployment**
   - [ ] `web/next.config.js` — Next.js optimization
   - [ ] `web/dockerfile` — Container image
   - [ ] Docker Compose for local testing
   - [ ] Kubernetes manifests for AKS

9. **Testing**
   - [ ] Unit tests for components
   - [ ] Integration tests with API mock
   - [ ] E2E tests (Playwright/Cypress)

10. **Deliverables**
    - Fully functional 6-panel dashboard
    - Real-time signal updates
    - Interactive drill-down (detail panel on row click)
    - Export to CSV/JSON
    - Mobile responsive

**Success Metrics**:
- Dashboard loads in <2 seconds
- Real-time updates within 5 seconds
- All 6 panels rendering correctly
- Mobile usable on tablets

---

### Sprint 6 (Weeks 11-12): Deployment & Monitoring

**Objective**: Production infrastructure, monitoring, documentation

**Tasks**:

1. **Infrastructure as Code**
   - [ ] `infra/kubernetes/deployment.yaml` — API service (3 replicas)
   - [ ] `infra/kubernetes/service.yaml` — Service + load balancer
   - [ ] `infra/kubernetes/configmap.yaml` — Configuration
   - [ ] `infra/kubernetes/secrets.yaml` — API keys, DB credentials (sealed)
   - [ ] Helm charts for reusable deployments

2. **Container Images**
   - [ ] `infra/docker/api.dockerfile` — Python FastAPI
   - [ ] `infra/docker/web.dockerfile` — Node.js Next.js
   - [ ] `infra/docker/worker.dockerfile` — Databricks feature jobs
   - [ ] Image scanning for vulnerabilities

3. **Monitoring & Observability**
   - [ ] `src/monitoring/logging.py` — Structured JSON logging
   - [ ] `src/monitoring/metrics.py` — Prometheus metrics
   - [ ] `src/monitoring/tracing.py` — Jaeger distributed tracing
   - [ ] Dashboards: Grafana for infra, custom dashboard for business metrics
   - [ ] Alerts: PagerDuty/Slack for critical issues

4. **Database**
   - [ ] PostgreSQL schema for Signal Book, P&L, audit logs
   - [ ] Backup & recovery procedures
   - [ ] Replication to analytics (Snowflake)

5. **CI/CD**
   - [ ] GitHub Actions or Azure Pipelines
   - [ ] Automated tests on every PR
   - [ ] Code coverage enforcement (>80% for signal logic)
   - [ ] Container image builds
   - [ ] Automated deployment to DEV/QA/PROD

6. **Documentation**
   - [ ] API documentation (Swagger/OpenAPI)
   - [ ] Deployment runbooks
   - [ ] Troubleshooting guides
   - [ ] Feature engineering documentation
   - [ ] Model training & retraining guide

7. **Security & Compliance**
   - [ ] Penetration testing
   - [ ] SAST/DAST scanning
   - [ ] Data encryption validation
   - [ ] Audit log review
   - [ ] Security posture assessment

8. **Deliverables**
   - Production deployment on AKS
   - Monitoring dashboards live
   - CI/CD pipeline fully automated
   - Runbooks for ops team
   - Security audit passed

**Success Metrics**:
- 99.5% uptime SLA met
- Alert resolution <15 minutes
- Deployment time <5 minutes
- Zero critical security findings

---

## Phase 2: ML Enhancements (Weeks 13-18)

### Objectives:
- Regime detection (HMM/clustering on market microstructure)
- Automated hyperparameter tuning
- Feature drift monitoring & auto-retraining
- Ensemble methods (stacking, boosting)
- Expand to all 12 commodities

### Deliverables:
- Regime-aware signal filtering
- Automated retraining pipeline
- Feature importance tracking
- Enhanced model performance (target: 65%+ precision)

---

## Phase 3: Scale & Execution (Weeks 19-26)

### Objectives:
- Natural gas expansion
- Order Management System (OMS) integration
- Auto-execution on qualified signals
- Multi-desk federation
- Advanced visualization (3D term structures)

### Deliverables:
- OMS integration complete
- Auto-execution framework
- Multi-product support
- Enterprise dashboard features

---

## Key Milestones

| Week | Milestone | Status |
|------|-----------|--------|
| 2 | All 18 data sources ingesting | 🟡 In Progress |
| 4 | 100+ features in Feature Store | 🔴 Not Started |
| 6 | LightGBM models trained & backtested | 🔴 Not Started |
| 8 | FastAPI gateway with all endpoints | 🟡 In Progress |
| 10 | React dashboard live | 🔴 Not Started |
| 12 | Production deployment on AKS | 🔴 Not Started |

---

## Development Setup

### Local Environment

```bash
# Clone repo
git clone <repo> && cd marketsensing

# Python environment
python3.11 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"

# Node environment
cd web
npm install
npm run dev  # http://localhost:3000

# Python API
uvicorn src.api.main:app --reload  # http://localhost:8000

# Docker Compose (with Postgres, Redis, Databricks mock)
docker-compose up
```

### Database Setup

```bash
# PostgreSQL
psql -U postgres -d marketsensing -f infra/schema.sql

# Databricks (for Feature Store)
# Connect to workspace and initialize Feature Store tables
```

---

## Testing Strategy

### Unit Tests
- `tests/unit/test_models.py` — Domain model validation
- `tests/unit/test_features.py` — Feature engineering logic
- `tests/unit/test_ml.py` — Model training & inference
- `tests/unit/test_orchestration.py` — Signal generation

### Integration Tests
- `tests/integration/test_data_pipeline.py` — End-to-end ingestion → features → signals
- `tests/integration/test_api.py` — API endpoints with mocked backend
- `tests/integration/test_dashboard.py` — Frontend with API mock

### E2E Tests
- Real API server + dashboard
- Test signal flow from ingestion → API → frontend display
- Load testing with concurrent users

### Coverage
- Target: >80% for signal logic (critical path)
- Target: >70% for features, ML
- Target: >60% for API, infra

---

## Success Criteria

### Data Layer
- ✅ All 18 sources connected
- ✅ 213+ tables ingested into Bronze layer
- ✅ Zero data loss
- ✅ <1 hour feature store freshness

### ML Layer
- ✅ 50+ models trained & backtested
- ✅ ≥60% precision (directional accuracy)
- ✅ ≥1.5 Sharpe ratio
- ✅ Sharpe ratio matches historical ($13.4MM P&L)

### API Layer
- ✅ All 9+ endpoints implemented
- ✅ WebSocket real-time updates
- ✅ Auth/RBAC working
- ✅ <500ms p95 latency

### Frontend
- ✅ 6-panel dashboard rendering
- ✅ Real-time updates
- ✅ Interactive drill-down
- ✅ Mobile responsive

### Operations
- ✅ 99.5% uptime SLA
- ✅ <15min alert resolution
- ✅ <5min deployment time
- ✅ Zero critical security findings

---

## Team & Roles

### Data Engineering
- **Responsibilities**: Ingestion connectors, Bronze/Silver/Gold medallion, Feature Store
- **Team**: 2-3 engineers

### ML Engineering
- **Responsibilities**: Model training, evaluation, serving, monitoring
- **Team**: 1-2 engineers

### Backend Engineering
- **Responsibilities**: FastAPI gateway, Signal Book persistence, API design
- **Team**: 1 engineer

### Frontend Engineering
- **Responsibilities**: React dashboard, UX, mobile responsive
- **Team**: 1-2 engineers

### DevOps/SRE
- **Responsibilities**: Infrastructure, CI/CD, monitoring, security
- **Team**: 1 engineer

### Product/Analytics
- **Responsibilities**: Requirements, success metrics, stakeholder management
- **Team**: 1 PM + 1 analyst

---

## Resources & Tools

### Development Tools
- Python 3.11, Node.js 18+, TypeScript 5
- Docker, Kubernetes, Helm
- Git + GitHub, VSCode

### Cloud Services (Azure)
- Databricks (PySpark, Feature Store, MLflow)
- Azure Data Factory (orchestration)
- Azure SQL Server / PostgreSQL (persistence)
- Azure Event Hubs (streaming)
- Azure Container Registry (images)
- Azure Kubernetes Service (deployment)
- Azure Key Vault (secrets)

### Third-Party Libraries
- **Data**: PySpark, Pandas, NumPy, Delta Lake
- **ML**: LightGBM, Optuna, SHAP, scikit-learn
- **API**: FastAPI, Pydantic, Uvicorn
- **Frontend**: React, Next.js, Recharts, TanStack
- **Monitoring**: Prometheus, Grafana, Jaeger, structlog

### External Data
- Kpler API, EIA API, Weather Source API
- Database replicas (EIS, TMR, TRR, RDW, etc.)
- TickerTech (NYMEX futures)

---

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Data source API instability | High | Fallback caching, connector retry logic, SLA tracking |
| Model precision degradation | High | Drift detection, auto-retraining, backtesting on live data |
| Infrastructure unavailability | High | Multi-region redundancy, database replication, IaC versioning |
| Security breach | Critical | Encryption, audit logs, penetration testing, SOC 2 compliance |
| Integration delays (OMS, EH) | Medium | Parallel dev, mock OMS layer, API contracts early |
| Performance issues under load | Medium | Load testing, caching strategy, database indexing |

