---
name: code-review
description: Review code changes for MarketSensing project standards
---

# Code Review Skill

Review code changes against MarketSensing project standards.

## Checklist

1. **No hard-coded thresholds** — all trading parameters must come from config YAML files
2. **Type hints** — all function signatures must have type annotations
3. **Signal schema compliance** — signal outputs must match the canonical JSON schema
4. **Feature store contract** — features must be time-indexed and instrument-indexed
5. **Risk filter presence** — signal generators must pass through risk filters before output
6. **Test coverage** — signal logic must have corresponding pytest tests
7. **Delta Lake compatibility** — data operations must be idempotent and support replay
8. **Logging** — all signal generation must log with structured fields (strategy_id, instrument_id, timestamp)
9. **Configuration** — no environment-specific values in code; use config/ YAML files
10. **Docstrings** — public functions in signal and feature modules must have docstrings

## How to Run

```bash
# Review staged changes
git diff --cached --name-only | xargs -I {} echo "Reviewing: {}"
ruff check src/
pytest tests/ -x --tb=short
```
