# Team Roles Reference

This document defines team roles used in the MarketSensing platform. All personal names and company-specific references have been removed from documentation for security and privacy.

---

## Core Team Roles

| Role | Responsibility | Key Systems |
|------|---|---|
| **Platform Architect** | System design, data flow, scalability decisions | Architecture docs, ADRs, performance SLAs |
| **Data Engineer** | Ingestion pipelines, medallion architecture, data validation | Delta Lake, Feature Store, data connectors |
| **ML Engineer** | Model training, evaluation, serving, monitoring | LightGBM, MLflow, backtesting, precision metrics |
| **Backend Engineer** | FastAPI, signal orchestration, database persistence | PostgreSQL, Redis, REST API, signal book |
| **Frontend Engineer** | React dashboard, UX, real-time updates | React.js, TypeScript, WebSocket, visualizations |
| **DevOps/SRE** | Infrastructure, CI/CD, monitoring, reliability | Kubernetes, Docker, Prometheus, Grafana |
| **Product Manager** | Requirements, success metrics, stakeholder management | Roadmap, KPIs, signal performance tracking |

---

## Internal Systems Mapping (Fictional)

These generic descriptors replace company-specific system names:

| Generic Name | System Type | Purpose |
|---|---|---|
| **Internal Production Forecasts** | Operations Planning | Predict refinery production 1-3 weeks ahead |
| **Internal Sales Forecasts** | Demand Planning | Forecast customer demand and volume |
| **Transportation Cost Index** | Logistics | Pipeline, barge, and vessel rate tracking |
| **Deal Tracking System** | Execution History | Log and analyze completed trades |
| **Risk Tracking Dashboard** | Risk Management | Monitor positions, P&L, portfolio limits |
| **Maintenance Schedule DB** | Operations | Refinery turnaround and maintenance calendar |

---

## Data Sources (Company-Agnostic)

All data sources are referenced by their public provider name:

- **NYMEX** — Exchange futures data
- **EIA** — US Energy Information Administration reports
- **Kpler** — Commercial tanker tracking service
- **Platts/Argus** — Third-party price assessments
- **CFTC** — Commitment of Traders reports
- **Weather Services** — Temperature and precipitation data
- **Third-party Analytics** — Market intelligence and research

---

## Organizational Hierarchy

- **Trading Organization** — Fictional petroleum trading desk (referred to as "the organization" in docs)
- **Data & Analytics Team** — Supports signal generation and infrastructure
- **Risk Management** — Oversees compliance, position limits, and risk controls
- **Operations** — Manages infrastructure and deployment

---

## Version History

- **2026-08-09**: Created roles reference; removed all personal names, emails, and company-specific identifiers from documentation
- All subsequent documentation uses role titles and generic system names
