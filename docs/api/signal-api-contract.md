# Signal API Contract

## Base URL
`/api/v1`

## Authentication
Bearer token (JWT) — configured per environment.

## Endpoints

### GET `/signals/latest`
Returns the most recent signals across all active strategies.

**Query Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `limit` | int | 20 | Max signals to return |
| `min_confidence` | float | 0.0 | Filter by minimum confidence |
| `strategy_type` | string | null | Filter: location_spread, time_spread, crack_spread |

**Response:**
```json
{
  "signals": [
    {
      "signal_id": "550e8400-e29b-41d4-a716-446655440000",
      "timestamp": "2026-03-20T14:30:00Z",
      "strategy_id": "spread_midland_cushing",
      "instrument_long": "WTI_MIDLAND",
      "instrument_short": "WTI_CUSHING",
      "action": "enter",
      "side": "long_spread",
      "size": 10,
      "confidence": 0.82,
      "expected_hold_time": "3d",
      "rationale": "Spread at -2.1 sigma below 60d mean",
      "model_version": "v1.2.0",
      "risk_checks_passed": true
    }
  ],
  "count": 1,
  "as_of": "2026-03-20T14:30:05Z"
}
```

### GET `/signals/{strategy_id}`
Returns signals for a specific strategy.

### GET `/signals/instrument/{instrument_id}`
Returns all signals involving a specific instrument.

### GET `/signal-book`
Returns the full ranked Signal Book — all active signals sorted by confidence.

**Response:**
```json
{
  "signal_book": [...],
  "total_active": 5,
  "portfolio_utilization_pct": 42.0,
  "regime": "normal_mean_reverting",
  "generated_at": "2026-03-20T14:30:05Z"
}
```

### GET `/health`
```json
{
  "status": "healthy",
  "market_data_last_update": "2026-03-20T14:29:58Z",
  "features_last_update": "2026-03-20T14:30:00Z",
  "active_strategies": 5,
  "muted_strategies": 0,
  "kill_switches_active": []
}
```

### GET `/config/strategies`
Returns active strategy configurations (read-only).

## Error Responses
```json
{
  "error": "not_found",
  "message": "Strategy 'unknown_strategy' not found",
  "timestamp": "2026-03-20T14:30:05Z"
}
```

## HTTP Status Codes
| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad request (invalid params) |
| 401 | Unauthorized |
| 404 | Resource not found |
| 503 | Service unavailable (data pipeline down) |
