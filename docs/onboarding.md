# Market Sensing — Onboarding Guide for Data Engineers

A ground-up walkthrough of the platform, written for engineers coming from a
data-engineering background. It starts from familiar mental models (medallion
layers, schemas, pipelines) and bridges up into the trading domain and the ML.

> **Scope note:** This guide describes the *architecture and design concepts* of
> the Market Sensing platform as represented in this repository. It is generic by
> design and contains no confidential business data, results, or vendor specifics.

---

## 0. The one-sentence essence

> Market Sensing is a **production ML pipeline that reads market data, predicts the
> future value of price *spreads*, and converts those predictions into
> Buy / Sell / Hold signals** for commercial traders — built on top of a standard
> medallion data platform.

Everything below unpacks that sentence. Before the schemas mean anything, you need
the **domain**: every table in this system exists to serve a trading idea.

---

## 1. The domain: what oil traders actually do

A commercial trading desk makes money on **arbitrage**:

> **Arbitrage = buy something now, sell it later (or elsewhere), with net-zero change
> to physical inventory.** You are exposed to price moves only until you "unwind" the
> position.

The key mental shift: traders rarely bet on the **outright price** of oil. They bet
on **spreads** — the *difference* between two related prices. Why?

- A spread is **lower-risk and mean-reverting** — two linked prices wander in a tight
  band; an outright price can go anywhere.
- A spread maps directly to a **physical trade** the desk can execute (buy here, sell
  there).

### Vocabulary

| Term | Plain meaning | Example |
|---|---|---|
| **Spread** | price of leg A − price of leg B | Houston crude − Cushing crude |
| **Leg** | one side of the spread (what you buy or sell) | "Cushing crude" |
| **Long the spread** | bet the spread *widens* (buy A, sell B) | profit if A rises vs B |
| **Short the spread** | bet the spread *narrows* | profit if the gap closes |
| **Unwind** | close both legs, lock the P&L | — |

### The three kinds of spread (the three "arbitrage dimensions")

1. **Time arbitrage** — same product, **different delivery dates**. Buy the near month,
   sell the far month (or vice versa).
   - **Contango** = far month *more expensive* than near (market pays you to store).
   - **Backwardation** = near month *more expensive* than far (market wants oil *now*).

2. **Location / geographic arbitrage** — same product, **different hubs/regions**. Buy
   where it's cheap, sell where it's dear (e.g. between two physical pricing hubs).

3. **Crack-spread / refining arbitrage** — **crude vs the refined products** made from
   it. The "3-2-1 crack" = 3 barrels crude → 2 gasoline + 1 diesel. This *is* a
   refiner's margin, so hedging it is core business.

**The whole system exists** to tell a trader, systematically and across many
commodities and horizons at once, *which spreads are about to move and in which
direction* — replacing fragmented manual analysis.

---

## 2. What the system produces (the output)

The end product is a **signal**, surfaced in a BI dashboard:

```
Spread:  ULSD region-A vs region-B,   horizon: 30 days
Predicted spread:  +2.40 $/bbl   (model output)
Current spread:    +1.10 $/bbl
→ SIGNAL: LONG   (predicted >> current, crosses the threshold)
```

Signal quality is judged on two ideas worth internalizing:

- **Directional precision** — of the times it said "Long," how often the spread
  actually rose. (Above 50% = an edge.)
- **Sharpe ratio** — return per unit of risk. Higher is better.

See [api/signal-api-contract.md](api/signal-api-contract.md) for the full signal schema
and REST contract.

---

## 3. End-to-end architecture (the map)

The left half is the **data-engineering world**; the right half is the **ML / serving
world**.

```
        ┌─────────── DATA ENGINEERING ───────────┐   ┌──── ML / SERVING ────┐

 Sources         Bronze          Silver        Semantic        Model          Output
 ───────         ──────          ──────        ────────        ─────          ──────
 market data,    raw      ──►    conformed ──► feature   ──►   spread     ──► threshold ──► BI
 fundamentals,   replicas        facts +       views          regressors     → L/N/S       dashboard
 prices,                         dims          (the model's   (1 per pair)   + backtest
 weather, ...                                   input)                         metrics
```

The single most important DE fact in the system:

> **The semantic / feature-view layer IS the model's input.** The model does not read
> Bronze or Silver — it reads the semantic views. That makes the semantic layer the
> **contract** between Data Engineering and the model.

---

## 4. The data backbone (your home turf)

### 4.1 Medallion layers

| Layer | Holds | DE concern |
|---|---|---|
| **Bronze / raw** | 1:1 replicas of source systems, untouched | ingestion, schema drift, replayability |
| **Silver / core** | cleaned, conformed, modeled as **facts + dimensions** | conforming keys, dedup, MDM, data quality |
| **Semantic / feature** | business-friendly **feature views** the model consumes | schema stability, feature correctness — *the contract* |
| **Restricted** | P&L / risk views, access-controlled | governance, access provisioning |

Silver uses classic dimensional modeling (`*_Fact` / `*_Dim`) — familiar territory.
See the schema docs: [schemas/bronze.md](schemas/bronze.md),
[schemas/silver.md](schemas/silver.md), [schemas/gold.md](schemas/gold.md).

### 4.2 Source categories

The platform blends several families of inputs (exact vendors vary by deployment):

| Category | Provides |
|---|---|
| Government statistics (e.g. EIA) | inventories, production, demand |
| Vessel / cargo tracking | physical flows and trades |
| Infrastructure / flow monitoring | real-time operational data |
| Internal commercial systems | the desk's own positions and plans |
| Market intelligence & weather | forecasts, prices, weather |

### 4.3 Recurring DE risks to watch

- **Methodology breaks in historical data** — public sources can change definitions
  over time; watch for silent discontinuities in long time series.
- **Source substitution / gaps** — when one source lacks coverage (region or history),
  another is substituted. Keep lineage explicit.
- **Schema validation of the semantic layer** — the DE↔model contract; the
  highest-leverage thing the DE owns.
- **Access / governance for restricted (risk/P&L) data.**

---

## 5. The ML, explained for a Data Engineer

You don't need to be an ML researcher to own this. Think of the model as **a function
that maps a feature row to a number**, plus a calibration step.

### 5.1 The model

> **One gradient-boosted regressor (e.g. LightGBM) per commodity-contract pair**, which
> scales to **many models** (commodities × contracts × horizons).

- **LightGBM** = gradient-boosted decision trees: a fast, tabular model. Give it a wide
  feature table, it learns. No GPUs. The industry default for structured data.
- **One model per pair** — each spread gets its *own* dedicated regressor. This is why
  the hard part is **MLOps, not modeling** (training / versioning / serving / monitoring
  many models — a fan-out problem the platform must solve).

### 5.2 What each model predicts

```
Spread(horizon) = f(fundamentals)
```

"Given today's fundamentals, predict what this spread will be `horizon` days out." The
features are rows from the semantic views; the label is the actual historical spread
value at the future date.

### 5.3 The most important ML insight in this system

> The model is a **regressor**, but the *product* is a **classifier**. Threshold
> calibration is a **separate lever** from model fit.

| Stage | Does | Metrics |
|---|---|---|
| **1. Regression** | predict the spread *value* | **RMSE** (training objective), **R²**, **MAE** |
| **2. Thresholding** | predicted value → **Long / Neutral / Short** | **precision, recall, F1** (Buy/Sell confusion matrix) |

A mediocre regressor with a well-tuned threshold can still produce a great signal — and
vice versa. The threshold is a cheap, separate knob. For anyone moving into MLE work,
**threshold calibration on backtests is the highest-ROI, lowest-cost lever available.**

### 5.4 Validation: backtesting

Run the model over history, generate the signals it *would* have produced, compare to
what actually happened → build a Buy/Sell confusion matrix → compute precision / recall /
F1 plus trading metrics (directional precision, Sharpe). This is the gate before
anything goes live.

---

## 6. This repository (the scaffold)

This repo is a **clean-room model of the architecture at small scale** — a sandbox for
building the single-pair template that a production platform fans out to many models.

| Area | What's here |
|---|---|
| [config/](../config/) | instruments, strategies, risk limits — the design is config-driven |
| [docs/](.) | architecture, ADRs, medallion schemas, API contract, runbooks |
| [src/](../src/) | module layout: ingestion, features, signals, orchestration, api, persistence, monitoring |

Concretely defined today:

- **Instruments** — [config/instruments.yaml](../config/instruments.yaml)
- **Strategies** — [config/strategies.yaml](../config/strategies.yaml) (z-score spread
  rules; the simple, rules-based baseline before ML)
- **Risk controls** — [config/risk_limits.yaml](../config/risk_limits.yaml)
- **Signal schema + REST API** — [api/signal-api-contract.md](api/signal-api-contract.md)

Design rationale lives in the ADRs:
[medallion](decisions/001-medallion-architecture.md),
[config-driven signals](decisions/002-config-driven-signals.md),
[signal-only v1](decisions/003-signal-only-v1.md). Project conventions and the full
structure are in the root [CLAUDE.md](../CLAUDE.md).

---

## 7. Local-first, platform-aware ML approach

A recommended way to build the ML so it ports cleanly to a managed platform
(e.g. Databricks):

**Build ONE commodity-contract pair end-to-end locally** as the reference template
(`features → regressor → threshold → signal → backtest`). LightGBM trains in seconds on
a laptop — that fast inner loop is where ML intuition comes from. The platform's job is
then to **fan that one template out to many models and serve them**.

Enforce three portability seams so the lift is mechanical, not a rewrite:

| Seam | Local | Managed platform |
|---|---|---|
| **Feature access** | Parquet / DuckDB behind a `FeatureProvider` interface | semantic Delta views |
| **Tracking / registry** | **MLflow** local file store | **same MLflow API** → model registry |
| **Many-model fan-out** | loop / joblib | platform workflows (one run per pair) |
| **Serving** | `predict()` behind the API | managed model serving / batch scoring |

Using **MLflow from day one** is the biggest lever — identical API locally and on the
platform, so a model logged on a laptop registers to the managed registry with a config
change, not a rewrite.

---

## 8. Suggested learning path (DE → owning the system)

1. **Map the semantic contract** — list the feature views and exactly which columns each
   model consumes. This is the DE↔model contract; own it cold.
2. **Trace one pair end-to-end** — pick a single spread and follow the lineage: source →
   raw → conformed facts → feature view → model → signal. One full thread teaches the
   whole system.
3. **Build the regression→threshold split hands-on** — a local single-pair pipeline
   (synthetic data, LightGBM, MLflow, backtest) makes the two-stage design concrete.
4. **Learn the many-model MLOps pattern** — workflows + model registry + serving to fan
   one template out, version, serve, and monitor drift.
5. **Then the frontier** — regime detection as a gating feature, and an agentic/LLM
   layer on top.
