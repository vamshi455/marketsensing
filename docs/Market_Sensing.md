# Market Sensing
## Turning Predictive Signals into Trading Decisions

**Authors:** Sam Fuqua, Greg Meffert & Raghva Vishnubhotla

*Source: `Market_Sensing.pdf` — 10 slides. Text from slide bodies, speaker-visible labels, and text rendered inside dashboard screenshots is preserved below.*

---

## Slide 2 — Understanding Market Sensing

**Anticipating Market Trends**
Market Sensing collects and interprets data to predict future trends, allowing MPC to profit on future changes

**Data Ingestion**
Market Sensing ingests both internal and external data to support informed decision making

**Supporting Strategic Decisions**
Market Sensing enables timely strategic decisions, enhancing adaptability and maintaining a competitive advantage.

**Total Impact = $13.4 MM realized profits**
- 12 Commodities with 63% precision in direction and 1.94 Sharpe Ratio

*(Slide graphic: illustration of dashboards/charts on desktop and mobile screens with a magnifying glass.)*

---

## Slide 3 — Market Sensing | Road Map

*(Organization-branded header with company logo.)*

Timeline columns: **1H 25 · 2H 25 · 1H 26 · 2H 26**

| Swimlane | 1H 25 | 2H 25 | 1H 26 | 2H 26 |
|---|---|---|---|---|
| **Targeted Value** | Time and Geo Arb – Light Products *(In Implementation)* | Time and Geo Arb – Light Products Signal Optimization *(Hypercare)* | — | — |
| **Targeted Value** | — | Time Arb – Butane & Propane *(In Implementation)* | Butane & Propane *(Hypercare)* | — |
| **Targeted Value** | — | — | Time/Geo Arb - Product TBD *(In Discovery)* | Time/Geo Arb - Product TBD *(In Implementation)* |
| **Platform Enablement** | — | Optimized thresholds and Signal Consolidation *(In Implementation)* | Regime Detection *(In Discovery, extends across 1H 26–2H 26)* | Regime Detection *(cont.)* |
| **Data Enablement** | — | Weather Data Enhancements *(In Implementation)* | — | — |
| **Data Enablement** | — | — | Sentiment Data Feature Exploration *(In Discovery)* | — |

**Key:**
- In Implementation *(green)*
- Hypercare *(dark green)*
- In Discovery *(blue)*

---

## Slide 4 — Rolls and Spreads

**Left column — Rolls**
- Rolls involve simultaneous buying near-term and selling far-term barrels
- Must physically receive or deliver barrels
- Executing rolls results in no net position change but impacts cycle inventory.
  - Manage cycle inventory by buying/selling length or Exchange for Physical (EFP)
- Rolls help capture market value between cycles as an easier alternative to outright purchases or sales
- Trading rolls within the same month limits exposure solely to basis risk
  - Price = Merc (NYMEX) + basis

**Right column — Spreads**
- Time Spreads = buy a near term & sell a far term simultaneously
  - Swaps, Futures
- Geo Spreads = buy one product in one region and an equivalent product in another region
- Swaps are a pure financial instrument that measure the price of a commodity at one location compared to another
  - LT Swap = NYH ULSD vs GFC ULSD
  - Settle at every month
- Can be used to hedge physicals
  - Buy NYMEX HO future to hedge against price changes
  - Buy LT to "swap" from GFC basis to NYH basis

**Graphic labels**
- *Time Spread chart:* Y-axis "Price, $"; X-axis "Time"; series legend "November Price", "December Price"; annotations "Buy low" (left), "Sell high" (right)
- *Barrel diagram:* "$80" barrel → "$85" barrel; "Future Price Higher"; "Time Spread"
- *US map diagram:* "West Coast $75", "East Coast $85", "Price Difference +$10", "Geographic Spread"

---

## Slide 5 — Rolls and Spreads (Arbitrage)

- Arbitrage is a strategy to buy now and sell later
  - Results in net 0 inventory change
    - Exposed until you unwind
  - Time Arb
    - More value on derivatives market
    - Thought is that one trading period is going to get stronger or weaker compared to another trading period
    - Domestic Trading team
  - Geo Arb
    - Thought is that one region will strengthen over another region (US/ Europe or Asia/Europe)
    - International Trading team

*(Slide graphic: dark blue/green candlestick chart visualization.)*

---

## Slide 6 — Market Sensing
### • Turning Predictive Signals into Trading Decisions

| Section | Content |
|---|---|
| **Problem** | • Traders rely on fragmented, manual analysis across tools, limiting speed and consistency in identifying time and geographic arbitrage opportunities.<br>• There is no unified way to interpret predictive signals across commodities and forecast horizons. |
| **Solution** | • A centralized Power BI dashboard that integrates 100+ machine-learning models across 12 commodities and 1–90+ day horizons.<br>• Dashboard surfaces buy/sell signals, forward curves, spreads, and market indicators in one place. |
| **Benefits** | • **Faster decisions**: Near real-time signals reduce manual analysis and reaction time.<br>• **Improved margins**: Clear visibility into time and geo arbitrage opportunities supports better trade execution.<br>• **Efficiency & scale**: Automated, standardized insights that scale across desks and regions. |
| **Users** | • Commercial traders and analysts across MPC trading desks. |

*(Icons shown for Problem, Solution, Benefits, Users.)*

---

## Slide 7 — Market Sensing
### • Turning Predictive Signals into Trading Decisions

**Callout box (left):**

Market Sensing uses internal and external data for traders to systematically predict and act on market shifts. Initial Wave 1 efforts target over $30MM in annual value while improving efficiency and margin. *However, due to market conditions, the model produced 12M+ in revenue last month alone.* (underlined/italic emphasis in original)

An ML model developed by BCG was delivered in the Dev environment. **3Q25 required a strong collaboration between Data Engineering, Business Intelligence, Data Science, and MLOps members to stabilize the system into Production env.**

**Dashboard screenshot contents (right):**

Left nav rail (company logo): SIGNAL SUMMARY · *(chart icon)* · *(list icon)* · BACKTESTING · *(icons)* · → 

*Panel 1 — "Signals Overview for Model Run Date: 3/30/2026"*
Filters: Commodity = All · Spread = All · Model Run Date = Last Run

| Commodity | Contract | Today's Predicted State |
|---|---|---|
| HOGO | Jul 2026 | Short |
| LT | May 2026 | Long |
| | May 2026_Jun 2026 | Neutral |
| | Jun 2026 | Long |
| | Jun 2026_Jul 2026 | Neutral |
| | Jul 2026 | Long |
| | Jul 2026_Aug 2026 | Neutral |
| | Jul 2026_Sep 2026 | Short |
| | Aug 2026_Sep 2026 | Neutral |
| | Sep 2026_Oct 2026 | Neutral |
| NYH Barge Summer RBOB - F1 *(row partially cut off)* | Apr 2026 | Short |

*Panel 2 — "Spread View for Commodity: LT"*
Note (red text): "Values after the selected date (vertical line) are forecasted values. Values on or before the selected date are historical price spreads."

Tooltip at 06/25/2026:
| Contract | Value |
|---|---|
| Jul 2026 | -10.42 |
| Jul 2026_Aug 2026 | -1.83 |
| Jun 2026_Jul 2026 | -4.06 |
| Aug 2026_Sep 2026 | -1.84 |
| Sep 2026_Oct 2026 | 0.87 |

Contract legend: May 2026 · May 2026_Jun 2026 · Jun 2026 · Jun 2026_Jul 2026 · Jul 2026 · Jul 2026_Aug 2026 · Jul 2026_Sep 2026 · Aug 2026_Sep 2026 · Sep 2026_Oct 2026
Y-axis ticks: 5, 0, -5, -10, -15 · X-axis ticks: Nov 2025, Jan 2026, Mar 2026, May 2026, Jul 2026

---

## Slide 8 — Data Engineering

**Data categories (left):**
- **Supply** — Refinery production, import and exports
- **Demand** — Sales and consumption of products
- **Inventory** — Static storage and in-transit volumes
- **Production Costs** — Production (refining) costs, storage costs
- **Transport Costs** — Transportation (pipeline, rail, …) costs
- **Macroeconomic** — Broader macroeconomic data e.g., CPI, SP500
- **Non-Commodity** — External data e.g., weather

**Callout (green oval):** 213 Tables & Corresponding Views Implemented for Wave 2

**Callout (green box):** Aggregated data and views from 11 different sources **(EIA, Genscape, Kpler, KH, MPR, Planning DB, EIA, IIR, CFTC, Weather)**

**Dashboard screenshot contents (right):**

*Panel 1 — "Market Signal Summary"*
Filters: Commodity = LT · Contract = May 2026 · Type = Optimal · Signal = All · Trade Entry Date = All · Trade Exit Date = All · Model Run Date = Last Run

Header: "Optimal Signals for Model Run Date: 3/27/2026"
Disclaimer (red): "*Buy/sell signals are model-generated outputs and should be used as directional guidance only. Please apply trading judgment and market context before acting on these insights."

| Commodity | Contract | Trade Entry Date | Trade Exit Date | Signal | Settle Price (cpg) | Entry Price | Predicted Spread | Predicted Margin Opt. | Bid/Ask (cpg) | Entry Price Incl. Bid-Ask |
|---|---|---|---|---|---|---|---|---|---|---|
| LT | May 2026 | 03/03/2026 | 03/31/2026 | Buy | -12.25 | -10.33 | -8.40 | 1.43 | 0.50 | -9.83 |
| LT | May 2026 | 03/05/2026 | 04/02/2026 | Buy | -12.25 | -10.50 | -8.40 | 1.60 | 0.50 | -10.00 |
| LT | May 2026 | 03/06/2026 | 04/06/2026 | Buy | -12.25 | -10.25 | -8.40 | 1.35 | 0.50 | -9.75 |
| LT | May 2026 | 03/09/2026 | 04/07/2026 | Buy | -12.25 | -10.38 | -8.37 | 1.51 | 0.50 | -9.88 |
| LT | May 2026 | 03/10/2026 | 04/08/2026 | Buy | -12.25 | -10.75 | -8.39 | 1.86 | 0.50 | -10.25 |
| LT | May 2026 | 03/11/2026 | 04/09/2026 | Buy | -12.25 | -10.00 | -8.35 | 1.15 | 0.50 | *(row cut off in screenshot)* |

*Panel 2 — "Forecast Distribution for Commodity: LT | May 2026"*
- CI % selector = 80%
- Legend: Sell (red) · Buy (green)
- Y-axis ticks: -10, -15 · X-axis ticks: Oct 2025, Nov 2025, Dec 2025, Jan 2026, Feb 2026, Mar 2026, Apr 2026
- Horizontal dashed threshold line shown

*Panel 3 — "Feature Impact for Commodity: LT | May 2026"* (waterfall)
Contribution values left→right: 74%, 6%, 6%, 5%, 3%, 2%, 2%, 2%, 1%, 0%, 0%, **Total 100%**
Feature axis labels (truncated in screenshot): Settled price · ewma_padd3_wee… · Near contract r… · ewma_padd3_net… · 30-day rolling … · 14-day rolling s… · ewma_padd3_end… · 14-day rolling s… · Days from anch… · Day of month · 20th percentile… · Total

---

## Slide 9 — Machine Learning

- LightGBM Regressor Model : Minimizing RMSE to fit closer to the target
- Metrics like R² (Coefficient of Determination) which measures the goodness of fit MAE (mean absolute error) which explains closeness of predictions and actual values
- Backtesting metrics such as precision, recall, and F1-score are critical for evaluating Signal performance

**Diagram 1 — target construction (left)**
- Current date · Anchor date (future date) · Leap duration (arrow between them)
- Fundamentals (X) · "Historical Data" (diagonal watermark text)
- Anchor period (M1_M2_y, ……, M11_M12_y)
- Contracts (Jan, ……, Dec)
- Target (y₁, y₂, y₃, …, yₙ)

**Diagram 2 — modeling flow (right)**
- Data for each leap duration (X, Spread) → Regression (lightgbm 50 models) — "Minimize RMSE" · scatter of Actual vs Predicted with R^2
- Convert → Trade signals — "Predicted > threshold" (candlestick chart with BUY/SELL markers)
- → Back test metrics

Confusion matrix ("Predicted Class" columns Buy / Sell; "Ground Truth" rows Buy / Sell):
| | Buy (predicted) | Sell (predicted) |
|---|---|---|
| **Buy (truth)** | True Positive (TP) | False Negative (FN) |
| **Sell (truth)** | False Positive (FP) | True Negative (TN) |

Formulas shown:
- Recall = TP / (TP + FN)
- Precision = TP / (TP + FP)
- F1 Score = 2 × (Precision × Recall) / (Precision + Recall)

Model equation: **Spread(y_leap duration) = f(fundamentals)**

---

## Slide 10 — Market Sensing

**Dashboard screenshot (left) — "Signals Overview for Model Run Date: 2/17/2026"**
Filters: Commodity = All · Spread = All · Model Run Date = Last Run
Left nav rail: SIGNAL SUMMARY · *(icons)* · BACKTESTING · *(icons)* · →

| Commodity | Contract | Today's Predicted State |
|---|---|---|
| LT | Aug 2026_Sep 2026 | Neutral |
| NYH Barge Summer RBOB - F1 | Apr 2026 | Neutral |
| | May 2026 | Neutral |
| | Jun 2026 | Neutral |
| NYMEX HO | Mar 2026_Apr 2026 | Long |
| | Apr 2026_May 2026 | Long |
| | May 2026_Jun 2026 | Long |
| | Jun 2026_Jul 2026 | Long |
| | Jul 2026_Aug 2026 | Long |
| | Aug 2026_Sep 2026 | Long |

*Spread View panel:* Contract legend = Mar 2026_Apr 2026 · Y-axis ticks 10, 5, 0 · X-axis ticks Aug 2025, Sep 2025, Oct 2025, Nov 2025, Dec 2025, Jan 2026, Feb 2026

**Executive Report screenshot (top right)**
Panel: "P&L" — Y-axis "Sum of Month MtM", ticks 0M / 10M

Monthly values (Jun 2025 → Mar 2026):
| Month | Value |
|---|---|
| June | -0.01M |
| July | 0.07M |
| August | 0.1M |
| September 2025 | 0.1M |
| October | 1.29M |
| November | 1.46M |
| December | 1.01M |
| January | 1.74M |
| February 2026 | 3.28M |
| March | 13.42M *(cumulative line label)* |

Product filter: All

| Product | MtM |
|---|---|
| SC | ($71,085) |
| Colonial CBOB physical | ($115,290) |
| Colonial ULSD physical | ($225,644) |
| CRB | ($26,460) |
| HOGO | $7,709,389 |
| LT | $158,025 |
| NYH Barge Winter RBOB - 15# *(label partially cut off)* | $54,810 |
| **Total** | **$13,419,934** |

**Callout box (right):**
**Total Impact = 13.4 MM realized profits**
- 12 Commodities with 63% precision in direction and 1.94 Sharpe Ratio

**Links (right):**
- Market Sensing Power BI
- Market Metrics Power BI
