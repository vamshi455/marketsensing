# Source Data Model - Logical & Physical Schema

Complete data model for all 18+ source systems. Use this as reference for synthetic data generation in PostgreSQL.

---

## 1. Market Data Sources

### 1.1 NYMEX Futures (TickerTech)

**Purpose**: Real-time futures pricing for WTI, RBOB, ULSD across multiple contract months

```sql
-- Bronze Layer Table
CREATE TABLE bronze.nymex_futures_ticks (
    tick_id BIGSERIAL PRIMARY KEY,
    data_source VARCHAR(50),           -- 'NYMEX'
    commodity_code VARCHAR(10),        -- 'WTI', 'RBOB', 'ULSD'
    contract_month VARCHAR(10),        -- 'JAN2026', 'FEB2026', etc.
    contract_year INTEGER,             -- 2026, 2027, etc.
    leap_duration_days INTEGER,        -- 1, 3, 7, 14, 30, 60, 90
    
    -- OHLCV Data
    open_price DECIMAL(10,4),
    high_price DECIMAL(10,4),
    low_price DECIMAL(10,4),
    close_price DECIMAL(10,4),
    volume_contracts INTEGER,
    
    -- Settlement & Bid-Ask
    settlement_price DECIMAL(10,4),
    bid_price DECIMAL(10,4),
    ask_price DECIMAL(10,4),
    bid_ask_spread DECIMAL(10,4),
    
    -- Metadata
    tick_timestamp TIMESTAMP WITH TIME ZONE,
    ingestion_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    data_quality_flag VARCHAR(20),     -- 'good', 'stale', 'suspicious'
    
    UNIQUE(commodity_code, contract_month, leap_duration_days, tick_timestamp)
);

-- Silver Layer Table (aggregated to daily)
CREATE TABLE silver.nymex_daily_bars (
    bar_id BIGSERIAL PRIMARY KEY,
    commodity_code VARCHAR(10),
    contract_month VARCHAR(10),
    bar_date DATE,
    open_price DECIMAL(10,4),
    high_price DECIMAL(10,4),
    low_price DECIMAL(10,4),
    close_price DECIMAL(10,4),
    volume_contracts BIGINT,
    settlement_price DECIMAL(10,4),
    
    UNIQUE(commodity_code, contract_month, bar_date)
);
```

**Key Dimensions**:
- Commodities: WTI, RBOB (gasoline), ULSD (diesel)
- Contract Months: F1 (front-month), F2, F3, F6, F12, etc.
- Frequency: Every second during trading hours
- Data Retention: Real-time ingestion, aggregated daily

---

### 1.2 Platts/Argus Physical Hub Prices

**Purpose**: Physical crude and product assessments at key US hubs

```sql
CREATE TABLE bronze.platts_argus_prices (
    price_id BIGSERIAL PRIMARY KEY,
    data_source VARCHAR(50),           -- 'Platts' or 'Argus'
    product_code VARCHAR(20),          -- 'WTI', 'Brent', 'RBOB', 'ULSD'
    location_hub VARCHAR(50),          -- 'Midland', 'Cushing', 'Houston/MEH'
    pricing_date DATE,                 -- Assessment date
    
    -- Price Data (per barrel)
    bid_price DECIMAL(10,4),
    ask_price DECIMAL(10,4),
    mid_price DECIMAL(10,4),           -- (bid + ask) / 2
    settle_price DECIMAL(10,4),
    
    -- Volume & Basis
    volume_traded DECIMAL(12,0),       -- barrels
    basis_vs_nymex DECIMAL(10,4),      -- Price - NYMEX equivalent
    
    -- Metadata
    publication_time TIMESTAMP WITH TIME ZONE,
    ingestion_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(data_source, product_code, location_hub, pricing_date)
);

-- Dim Table: Hubs and Locations
CREATE TABLE dim.location_hubs (
    location_id SERIAL PRIMARY KEY,
    hub_code VARCHAR(30),              -- 'Midland', 'Cushing', 'Houston'
    region VARCHAR(50),                -- 'West Texas', 'Oklahoma', 'Gulf Coast'
    state_code CHAR(2),                -- 'TX', 'OK', 'TX'
    pricing_point VARCHAR(100),        -- Full name for assessments
    is_active BOOLEAN DEFAULT TRUE
);
```

**Key Dimensions**:
- Hubs: Midland, Cushing, Houston/MEH, Corpus Christi, etc.
- Products: WTI Crude, RBOB Gasoline, ULSD Diesel, Brent, etc.
- Frequency: Daily (typically AM and PM assessments)
- Data Retention: 1+ year of daily prices

---

## 2. Supply Data Sources

### 2.1 Internal Production Forecasts (Planning DB)

**Purpose**: MPC refinery production forecasts and scheduled turnarounds

```sql
CREATE TABLE bronze.internal_production_forecasts (
    forecast_id BIGSERIAL PRIMARY KEY,
    source_system VARCHAR(50),         -- 'Planning DB', 'MPR/MIPS'
    refinery_code VARCHAR(20),         -- 'Garyville', 'Concordia', 'Catlettsburg', etc.
    forecast_date DATE,                -- Date forecast was created
    
    -- Production Metrics
    product_code VARCHAR(20),          -- 'Crude', 'RBOB', 'ULSD', 'HGO'
    planned_production_bbl DECIMAL(12,0),  -- barrels per day
    forecasted_production_bbl DECIMAL(12,0),
    actual_production_bbl DECIMAL(12,0),   -- filled when actual data received
    
    -- Operating Schedule
    refinery_run_rate_pct DECIMAL(5,2),    -- % of nameplate capacity
    is_scheduled_turnaround BOOLEAN,
    turnaround_start_date DATE,
    turnaround_end_date DATE,
    turnaround_duration_days INTEGER,
    expected_downtime_bbl DECIMAL(12,0),
    
    -- Metadata
    created_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ingestion_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    forecast_confidence_pct DECIMAL(5,2),  -- 60-100
    
    UNIQUE(refinery_code, product_code, forecast_date)
);

-- Dim Table: Refineries
CREATE TABLE dim.refineries (
    refinery_id SERIAL PRIMARY KEY,
    refinery_code VARCHAR(20),
    refinery_name VARCHAR(100),
    location_city VARCHAR(50),
    state_code CHAR(2),
    nameplate_capacity_bbl_day DECIMAL(12,0),
    products_produced VARCHAR(200),    -- RBOB, ULSD, HGO, etc.
    is_active BOOLEAN DEFAULT TRUE
);
```

**Key Dimensions**:
- Refineries: 4-6 US refineries (Garyville LA, Concordia KS, etc.)
- Products: Crude input, RBOB, ULSD, HGO, Asphalt, Petrochem
- Frequency: Daily/weekly updates
- Lookahead: 1-3 week forecasts, scheduled turnarounds weeks ahead

---

### 2.2 Competitor Production (EIA)

**Purpose**: EIA refinery output data (public)

```sql
CREATE TABLE bronze.eia_refinery_production (
    eid BIGSERIAL PRIMARY KEY,
    source_system VARCHAR(50),         -- 'EIA'
    report_date DATE,                  -- Weekly report date (Wednesdays)
    
    -- Region/PADD
    padd_code VARCHAR(10),             -- 'PADD 1' (East Coast), 'PADD 3' (Gulf), etc.
    
    -- Production by Product (barrels per day)
    crude_input_bbl_day DECIMAL(12,0),
    gasoline_production_bbl_day DECIMAL(12,0),
    diesel_production_bbl_day DECIMAL(12,0),
    heating_oil_production_bbl_day DECIMAL(12,0),
    
    -- Utilization
    refinery_utilization_pct DECIMAL(5,2),
    
    -- Metadata
    report_published_date TIMESTAMP WITH TIME ZONE,
    ingestion_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(report_date, padd_code)
);
```

**Key Dimensions**:
- PADDs: 5 districts (1=East, 2=Midwest, 3=Gulf, 4=Mountain, 5=West Coast)
- Frequency: Weekly (published Wednesdays, reflecting prior week)
- Data Age: 1-2 weeks lagged from actual date

---

### 2.3 Kpler Tanker Tracking (Physical Flows)

**Purpose**: Real-time crude and product shipments by vessel

```sql
CREATE TABLE bronze.kpler_trades (
    trade_id BIGSERIAL PRIMARY KEY,
    kpler_trade_id VARCHAR(50) UNIQUE,
    
    -- Vessel Info
    vessel_name VARCHAR(100),
    vessel_imo VARCHAR(20),
    vessel_type VARCHAR(50),           -- 'Supertanker', 'Aframax', 'Panamax'
    vessel_dwt INTEGER,                -- Dead weight tonnage
    
    -- Cargo Details
    product_name VARCHAR(50),          -- 'Crude Oil', 'Gasoline', 'Diesel'
    cargo_quantity_bbl DECIMAL(12,0),
    
    -- Route & Timing
    load_port VARCHAR(50),             -- Origin port (Valdez, Ceyhan, etc.)
    discharge_port VARCHAR(50),        -- Destination (Corpus Christi, Houston, etc.)
    load_date DATE,
    estimated_arrival_date DATE,
    actual_arrival_date DATE,
    
    -- Pricing
    freight_rate_per_bbl DECIMAL(10,4),
    trade_value_usd DECIMAL(15,2),
    
    -- Metadata
    reported_date DATE,
    data_freshness VARCHAR(20),        -- 'real-time', 'estimated', 'reported'
    ingestion_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(kpler_trade_id, load_date)
);

CREATE TABLE bronze.kpler_vessels (
    vessel_id BIGSERIAL PRIMARY KEY,
    vessel_imo VARCHAR(20) UNIQUE,
    vessel_name VARCHAR(100),
    vessel_type VARCHAR(50),
    built_year INTEGER,
    dwt INTEGER,
    teu_capacity INTEGER,              -- For container ships
    current_location VARCHAR(100),
    current_status VARCHAR(50),        -- 'Anchored', 'Underway', 'Discharging'
    last_update TIMESTAMP WITH TIME ZONE
);

CREATE TABLE bronze.kpler_port_calls (
    port_call_id BIGSERIAL PRIMARY KEY,
    vessel_imo VARCHAR(20),
    port_code VARCHAR(10),
    port_name VARCHAR(100),
    arrival_date TIMESTAMP WITH TIME ZONE,
    departure_date TIMESTAMP WITH TIME ZONE,
    cargo_bbl DECIMAL(12,0),
    operation_type VARCHAR(20)         -- 'Load', 'Discharge', 'Transit'
);
```

**Key Dimensions**:
- Vessel Types: Supertanker (300K bbl), Aframax (80-120K), Panamax (50-60K)
- Routes: Trans-Atlantic, Trans-Pacific, Intra-US, Gulf-Atlantic
- Frequency: Daily/real-time updates
- Key Flows: Cushing→Gulf, Midland→Gulf, Imports from West Africa/ME

---

## 3. Demand Data Sources

### 3.1 Internal Sales Forecasts (EIS)

**Purpose**: Customer demand forecasts by segment and geography

```sql
CREATE TABLE bronze.internal_sales_forecasts (
    forecast_id BIGSERIAL PRIMARY KEY,
    source_system VARCHAR(50),         -- 'EIS'
    
    -- Forecast Attributes
    forecast_date DATE,                -- Date forecast was created
    forecast_for_date DATE,            -- Date being forecasted
    
    -- Customer/Segment
    customer_segment VARCHAR(50),      -- 'Speedway', 'Wholesale', 'Commercial', 'Export'
    geography_region VARCHAR(50),      -- 'South', 'Midwest', 'Northeast', 'West'
    
    -- Product
    product_code VARCHAR(20),          -- 'RBOB', 'ULSD', 'HGO', 'Jet'
    
    -- Volume Forecast
    forecasted_demand_bbl DECIMAL(12,0),
    confidence_level_pct DECIMAL(5,2), -- 70-95
    
    -- Actuals (backfilled)
    actual_demand_bbl DECIMAL(12,0),
    variance_bbl DECIMAL(12,0),
    variance_pct DECIMAL(6,2),
    
    -- Metadata
    created_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ingestion_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(forecast_date, forecast_for_date, customer_segment, product_code, geography_region)
);

-- Dim Table: Customer Segments
CREATE TABLE dim.customer_segments (
    segment_id SERIAL PRIMARY KEY,
    segment_code VARCHAR(30),
    segment_name VARCHAR(100),
    channel_type VARCHAR(50),          -- 'Retail', 'Wholesale', 'Industrial'
    annual_volume_bbl DECIMAL(12,0)
);
```

**Key Dimensions**:
- Segments: Speedway (retail), Wholesale (jobbers), Commercial (large users)
- Products: RBOB, ULSD, HGO, Jet fuel
- Geography: Regional demand by supply point
- Frequency: Daily/weekly updates

---

## 4. Inventory & Logistics Data

### 4.1 Storage & Inventory Levels

**Purpose**: Tank levels, pipeline volumes, in-transit inventory

```sql
CREATE TABLE bronze.inventory_levels (
    inventory_id BIGSERIAL PRIMARY KEY,
    source_system VARCHAR(50),         -- Internal ops, EIA, Genscape
    
    -- Location & Product
    location_hub VARCHAR(50),          -- 'Cushing', 'Midland', 'Houston'
    product_code VARCHAR(20),          -- 'WTI', 'RBOB', 'ULSD'
    
    -- Inventory Snapshot
    snapshot_date DATE,
    tanks_in_storage_bbl DECIMAL(14,0),
    days_of_supply DECIMAL(6,2),
    
    -- Movement
    inbound_volume_bbl DECIMAL(12,0),  -- Expected inflows this week
    outbound_volume_bbl DECIMAL(12,0), -- Expected outflows this week
    
    -- Metadata
    confidence_level VARCHAR(20),      -- 'High', 'Medium', 'Estimated'
    ingestion_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

---

### 4.2 Transportation Cost Index (TRR)

**Purpose**: Pipeline, barge, and vessel rate tracking

```sql
CREATE TABLE bronze.transportation_costs (
    rate_id BIGSERIAL PRIMARY KEY,
    source_system VARCHAR(50),         -- 'TRR'
    
    -- Route
    origin_location VARCHAR(50),       -- 'Midland', 'Cushing'
    destination_location VARCHAR(50),  -- 'Houston', 'East Coast'
    transport_mode VARCHAR(20),        -- 'Pipeline', 'Barge', 'Truck', 'Rail'
    product_type VARCHAR(20),          -- 'Crude', 'Products'
    
    -- Rate Data ($/barrel)
    rate_per_bbl DECIMAL(8,4),
    min_rate_per_bbl DECIMAL(8,4),
    max_rate_per_bbl DECIMAL(8,4),
    avg_rate_per_bbl DECIMAL(8,4),
    
    -- Rate Period
    rate_date DATE,
    week_of_year INTEGER,
    
    -- Metadata
    data_freshness VARCHAR(20),
    ingestion_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(origin_location, destination_location, transport_mode, rate_date)
);

-- Barge-Specific Capacity
CREATE TABLE bronze.barge_capacity (
    barge_id BIGSERIAL PRIMARY KEY,
    barge_name VARCHAR(100),
    barge_capacity_bbl DECIMAL(12,0),
    barge_status VARCHAR(50),          -- 'Available', 'In Service', 'Maintenance'
    current_location VARCHAR(50),
    current_cargo_bbl DECIMAL(12,0),
    last_update TIMESTAMP WITH TIME ZONE
);
```

**Key Dimensions**:
- Routes: Cushing→Houston, Midland→Gulf, Pipeline vs Water
- Modes: Pipeline (cheap, slow to change), Barge (medium), Truck (expensive)
- Frequency: Daily/weekly updates

---

## 5. Deal Execution & P&L Tracking

### 5.1 Deal Tracking System (TMR)

**Purpose**: Executed trades, deal structures, P&L

```sql
CREATE TABLE bronze.executed_deals (
    deal_id BIGSERIAL PRIMARY KEY,
    deal_reference VARCHAR(50) UNIQUE,
    
    -- Deal Structure
    deal_type VARCHAR(50),             -- 'Spread', 'Outright', 'Swap', 'EFP'
    execution_date TIMESTAMP WITH TIME ZONE,
    
    -- Instruments
    long_instrument VARCHAR(100),      -- 'WTI_F1'
    short_instrument VARCHAR(100),     -- 'WTI_F3'
    
    -- Volumes & Prices
    volume_bbl DECIMAL(12,0),
    entry_price_long DECIMAL(10,4),
    entry_price_short DECIMAL(10,4),
    net_entry_spread DECIMAL(10,4),    -- Short - Long
    
    -- Exit/Settlement
    exit_date TIMESTAMP WITH TIME ZONE,
    exit_price_long DECIMAL(10,4),
    exit_price_short DECIMAL(10,4),
    
    -- P&L
    realized_pnl_usd DECIMAL(15,2),
    realized_pnl_per_bbl DECIMAL(8,4),
    
    -- Costs
    bid_ask_cost_usd DECIMAL(15,2),
    commissions_usd DECIMAL(10,2),
    
    -- Metadata
    trader_id VARCHAR(50),
    book_code VARCHAR(50),
    risk_classification VARCHAR(20),   -- 'Arbitrage', 'Hedge', 'Speculative'
    ingestion_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

**Key Dimensions**:
- Deal Types: Time Spread, Geo Spread, Crack Spread, Outright, Swaps
- Traders: Multiple (anonymized)
- Books: Commercial, Refining, Trading, Hedging

---

### 5.2 Risk Tracking Dashboard (RDW)

**Purpose**: Current positions, limits, exposures

```sql
CREATE TABLE bronze.risk_positions (
    position_id BIGSERIAL PRIMARY KEY,
    source_system VARCHAR(50),         -- 'RDW'
    
    -- Position Attributes
    snapshot_date DATE,
    snapshot_time TIMESTAMP WITH TIME ZONE,
    
    -- Instrument & Position
    commodity VARCHAR(20),             -- 'WTI', 'RBOB', 'ULSD'
    contract_month VARCHAR(10),
    position_bbl DECIMAL(13,0),        -- Long(+) or Short(-)
    
    -- P&L
    mark_to_market_usd DECIMAL(15,2),
    unrealized_pnl_usd DECIMAL(15,2),
    
    -- Risk Metrics
    delta_per_dollar DECIMAL(10,6),
    vega_per_dollar DECIMAL(10,6),
    notional_exposure_usd DECIMAL(16,2),
    
    -- Limits
    position_limit_bbl DECIMAL(13,0),
    limit_utilization_pct DECIMAL(5,2),
    risk_breach_flag BOOLEAN,
    
    -- Metadata
    book_code VARCHAR(50),
    ingestion_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

---

## 6. External Intelligence & Macro Data

### 6.1 Market Intelligence (IIR, WoodMac, etc.)

**Purpose**: News, analysis, macro trends

```sql
CREATE TABLE bronze.market_analysis (
    analysis_id BIGSERIAL PRIMARY KEY,
    source_system VARCHAR(50),         -- 'IIR', 'WoodMac', 'Bloomberg'
    
    -- Document Metadata
    report_date DATE,
    report_title VARCHAR(255),
    analysis_category VARCHAR(50),     -- 'Supply Outlook', 'Demand Trend', 'Geopolitical'
    
    -- Content
    key_findings TEXT,
    sentiment VARCHAR(20),             -- 'Bullish', 'Neutral', 'Bearish'
    
    -- Impacts
    affected_commodity VARCHAR(20),
    expected_impact_direction VARCHAR(10),  -- 'Up', 'Down', 'Volatile'
    impact_timeframe_days INTEGER,
    
    -- Metadata
    confidence_level_pct DECIMAL(5,2),
    ingestion_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

---

### 6.2 Macroeconomic Indicators

**Purpose**: CPI, FX, rates, GDP

```sql
CREATE TABLE bronze.macro_indicators (
    indicator_id BIGSERIAL PRIMARY KEY,
    source_system VARCHAR(50),         -- 'Fred', 'BLS', 'Census Bureau'
    
    -- Indicator
    indicator_code VARCHAR(50),        -- 'CPIAUCSL', 'DEXUSEU', 'DGS10'
    indicator_name VARCHAR(100),
    
    -- Values
    observation_date DATE,
    indicator_value DECIMAL(12,4),
    previous_value DECIMAL(12,4),
    percent_change DECIMAL(6,2),
    
    -- Metadata
    units VARCHAR(50),                 -- 'Index', 'Rate %', 'Count'
    frequency VARCHAR(20),             -- 'Monthly', 'Weekly', 'Daily'
    ingestion_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(indicator_code, observation_date)
);
```

---

### 6.3 Weather Data

**Purpose**: Temperature, precipitation for demand modeling

```sql
CREATE TABLE bronze.weather_observations (
    weather_id BIGSERIAL PRIMARY KEY,
    source_system VARCHAR(50),         -- 'Weather Source'
    
    -- Location
    location_code VARCHAR(10),         -- 'Chicago', 'NYC', 'LA'
    location_name VARCHAR(50),
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    
    -- Observations
    observation_date DATE,
    avg_temperature_f DECIMAL(5,2),
    high_temperature_f DECIMAL(5,2),
    low_temperature_f DECIMAL(5,2),
    precipitation_inches DECIMAL(6,2),
    
    -- Derived Features
    heating_degree_days INTEGER,       -- If temp < 65F
    cooling_degree_days INTEGER,       -- If temp > 65F
    departure_from_normal_f DECIMAL(5,2),
    
    ingestion_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(location_code, observation_date)
);
```

---

## 7. Genscape Real-Time Operations

**Purpose**: Refinery utilization before EIA reports

```sql
CREATE TABLE bronze.genscape_refinery_ops (
    genscape_id BIGSERIAL PRIMARY KEY,
    source_system VARCHAR(50),         -- 'Genscape'
    
    -- Refinery & Timing
    refinery_location VARCHAR(50),
    observation_date DATE,
    
    -- Operations
    crude_run_bbl_day DECIMAL(12,0),
    gasoline_production_bbl_day DECIMAL(12,0),
    diesel_production_bbl_day DECIMAL(12,0),
    utilization_rate_pct DECIMAL(5,2),
    
    -- Status Flags
    is_scheduled_maintenance BOOLEAN,
    maintenance_duration_days INTEGER,
    
    -- Metadata
    data_latency_hours DECIMAL(5,2),
    ingestion_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

---

## 8. Upstream Supply Data (Enverus)

**Purpose**: Production trends, rig counts

```sql
CREATE TABLE bronze.enverus_production (
    production_id BIGSERIAL PRIMARY KEY,
    source_system VARCHAR(50),         -- 'Enverus'
    
    -- Basin/Well
    basin_code VARCHAR(50),            -- 'Permian', 'Bakken', 'Eagle Ford'
    production_date DATE,
    
    -- Production (barrels per day)
    crude_production_bbl_day DECIMAL(12,0),
    natural_gas_mcf_day DECIMAL(12,0),
    
    -- Rig Counts
    active_oil_rigs INTEGER,
    active_gas_rigs INTEGER,
    
    -- Trends
    yoy_production_change_pct DECIMAL(6,2),
    
    ingestion_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(basin_code, production_date)
);
```

---

## 9. Dimension Tables (Core Reference)

```sql
-- Commodities Master
CREATE TABLE dim.commodities (
    commodity_id SERIAL PRIMARY KEY,
    commodity_code VARCHAR(20) UNIQUE,
    commodity_name VARCHAR(100),
    commodity_category VARCHAR(50),    -- 'Crude', 'Light Products', 'Heavy Products'
    uom VARCHAR(20),                   -- 'BBL', 'MWh', 'Metric Ton'
    pricing_point VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE
);

-- Contract Calendar
CREATE TABLE dim.contracts (
    contract_id SERIAL PRIMARY KEY,
    commodity_code VARCHAR(20),
    contract_month VARCHAR(10),        -- 'JAN2026', 'FEB2026'
    contract_year INTEGER,
    contract_sequence INTEGER,         -- 1=Jan, 2=Feb, etc.
    first_trading_day DATE,
    last_trading_day DATE,
    settlement_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    
    FOREIGN KEY (commodity_code) REFERENCES dim.commodities(commodity_code)
);

-- Time Dimension
CREATE TABLE dim.date_dimension (
    date_id SERIAL PRIMARY KEY,
    calendar_date DATE UNIQUE,
    year INTEGER,
    month INTEGER,
    day INTEGER,
    day_of_week INTEGER,               -- 0=Sunday, 6=Saturday
    week_of_year INTEGER,
    quarter INTEGER,
    is_weekday BOOLEAN,
    is_holiday BOOLEAN
);
```

---

## Relationships & Foreign Keys

```sql
-- Link price data to commodities
ALTER TABLE silver.nymex_daily_bars
ADD CONSTRAINT fk_nymex_commodity
FOREIGN KEY (commodity_code) REFERENCES dim.commodities(commodity_code);

-- Link physical prices to locations
ALTER TABLE bronze.platts_argus_prices
ADD CONSTRAINT fk_platts_location
FOREIGN KEY (location_hub) REFERENCES dim.location_hubs(hub_code);

-- Link production to refineries
ALTER TABLE bronze.internal_production_forecasts
ADD CONSTRAINT fk_forecast_refinery
FOREIGN KEY (refinery_code) REFERENCES dim.refineries(refinery_code);

-- Link forecasts to date dim
ALTER TABLE bronze.internal_sales_forecasts
ADD CONSTRAINT fk_forecast_date
FOREIGN KEY (forecast_date) REFERENCES dim.date_dimension(calendar_date);
```

---

## Synthetic Data Generation Guidance

### Volume Ranges (For Testing)
- **NYMEX Daily Volume**: 50K - 500K contracts
- **Physical Assessments**: $70 - $120 per barrel
- **Refinery Production**: 50K - 200K bbl/day per facility
- **Spread Values**: -$5 to +$5 per barrel
- **Transportation Costs**: $0.50 - $3.00 per barrel

### Temporal Patterns
- **Trading Hours**: 9:00 AM - 3:00 PM CT (NYMEX)
- **Report Release**: Wednesday 10:30 AM ET (EIA)
- **Tanker Transit**: 3-45 days depending on route
- **Refinery Turnarounds**: 2-6 week windows

### Realistic Correlations
- Higher production forecast → Lower forward curve backwardation
- Cold weather → Higher ULSD spreads
- Scheduled turnaround → Production spike in adjacent months
- Vessel supply tight → Higher transportation costs

---

## PostgreSQL Setup

```sql
-- Create schemas
CREATE SCHEMA IF NOT EXISTS bronze;
CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS gold;
CREATE SCHEMA IF NOT EXISTS dim;

-- Set search path
SET search_path TO bronze, silver, gold, dim, public;

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS pg_trgm;        -- Text search
CREATE EXTENSION IF NOT EXISTS btree_gist;     -- Exclusion constraints
```

---

## Version History

| Date | Change |
|------|--------|
| 2026-08-09 | Extracted from sources.xlsx; created comprehensive logical & physical model |
| N/A | Ready for synthetic data generation |

