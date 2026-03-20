---
name: refactor
description: Refactor MarketSensing code for clarity, performance, and maintainability
---

# Refactor Skill

Refactor code while preserving signal correctness and trading logic integrity.

## Guidelines

1. **Never change signal output behavior** without explicit approval
2. **Preserve feature store contracts** — column names, types, and indices are API boundaries
3. **Extract configuration** — move any discovered hard-coded values to config YAML
4. **Simplify spread calculations** — prefer vectorized pandas/PySpark over loops
5. **Consolidate duplicate logic** — especially across similar signal strategies
6. **Maintain test parity** — every refactored module must pass existing tests

## Safety Checks

- Run backtests before and after refactor to verify signal equivalence
- Compare feature distributions (mean, std, null counts) pre/post refactor
- Verify config YAML loads correctly after any schema changes
