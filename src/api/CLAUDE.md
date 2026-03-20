# API Module

FastAPI-based REST API for serving trading signals.

## Responsibilities
- Expose the Signal Book as queryable endpoints
- Serve real-time and historical signals by strategy, instrument, or time range
- Configuration management endpoints (read-only in v1)
- Health checks and signal freshness monitoring

## Endpoints (v1)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/signals/latest` | Latest signals across all strategies |
| GET | `/signals/{strategy_id}` | Signals for a specific strategy |
| GET | `/signals/instrument/{instrument_id}` | Signals for a specific instrument |
| GET | `/signal-book` | Full ranked Signal Book |
| GET | `/health` | API and signal pipeline health |
| GET | `/config/strategies` | Active strategy configurations |

## Signal Response Schema

```json
{
  "signal_id": "uuid",
  "timestamp": "ISO-8601",
  "strategy_id": "string",
  "instrument_long": "string",
  "instrument_short": "string",
  "action": "enter | exit",
  "side": "long_spread | short_spread",
  "size": "number",
  "confidence": "0.0-1.0",
  "expected_hold_time": "string",
  "rationale": "string",
  "model_version": "string",
  "risk_checks_passed": "boolean"
}
```
