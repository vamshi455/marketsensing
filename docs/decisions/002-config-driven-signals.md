# ADR-002: Configuration-Driven Signal Parameters

## Status
Accepted

## Context
Trading strategies require frequent tuning of thresholds, lookback windows, and risk limits. Hard-coding these values makes iteration slow and error-prone.

## Decision
All signal parameters, risk limits, and strategy definitions are stored in **YAML configuration files** under `config/`. No trading parameters are hard-coded in Python source.

Configuration files:
- `instruments.yaml` — instrument definitions
- `strategies.yaml` — strategy parameters and thresholds
- `risk_limits.yaml` — position limits, kill switches
- `schedules.yaml` — ingestion and computation schedules

## Consequences
- Strategy tuning requires only config changes, no code deploys
- Config files are version-controlled alongside code
- Validation layer needed to catch invalid config before deployment
- Risk of misconfiguration — mitigated by schema validation and CI checks
