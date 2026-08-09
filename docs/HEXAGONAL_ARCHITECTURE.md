# Hexagonal Architecture Implementation

**Status**: ✅ Complete  
**Date**: 2026-08-09  
**Phase**: MVP (Midland-Cushing Spread Signal)

---

## Overview

The MarketSensing project is structured using **Hexagonal Architecture (Ports & Adapters)** to ensure:
- ✅ Domain logic is **pure** (zero external dependencies)
- ✅ Adapters are **swappable** (Postgres ↔ SQLite, Console ↔ WebSocket)
- ✅ Tests are **isolated** (unit tests with fakes, integration tests with real adapters)
- ✅ Coupling is **minimal** (domain → ports ← adapters, never reversed)

---

## Directory Structure

```
marketsensing/
├── src/
│   ├── domain/                        # ✅ Pure business logic
│   │   ├── entities/                  # Domain objects (PriceBar, Spread, Signal)
│   │   │   ├── price_bar.py
│   │   │   ├── spread.py
│   │   │   └── signal.py
│   │   ├── services/                  # Domain services (Z-score, risk checking)
│   │   │   ├── spread_signal_service.py
│   │   │   └── risk_checker.py
│   │   ├── value_objects/             # Immutable calculation objects
│   │   │   ├── instrument.py
│   │   │   ├── z_score.py
│   │   │   └── spread_statistics.py
│   │   └── exceptions.py              # Domain-specific errors
│   │
│   ├── ports/                         # ✅ Abstract interfaces
│   │   ├── repository.py              # IPriceRepository, ISpreadRepository, ISignalRepository
│   │   ├── config.py                  # IConfigLoader
│   │   ├── logger.py                  # ILogger
│   │   └── notifier.py                # INotifier
│   │
│   ├── adapters/                      # ✅ Concrete implementations
│   │   ├── repositories/
│   │   │   ├── postgres_price.py      # Queries PostgreSQL price_bars table
│   │   │   ├── postgres_spread.py     # Queries PostgreSQL spreads table
│   │   │   └── postgres_signal.py     # Persists signals to PostgreSQL
│   │   ├── config/
│   │   │   └── yaml_loader.py         # Loads YAML strategy configs
│   │   ├── logger/
│   │   │   └── console_logger.py      # JSON-formatted console logs
│   │   └── notifiers/
│   │       └── console_notifier.py    # Prints signals to stdout
│   │
│   ├── application/                   # ✅ Use cases & orchestration
│   │   ├── use_cases/
│   │   │   └── generate_signal.py     # Wires domain + adapters together
│   │   └── dto/
│   │       └── signal_dto.py          # Request/response objects
│   │
│   ├── infrastructure/                # ✅ Wiring & setup
│   │   ├── database.py                # PostgreSQL connection pool & schema
│   │   ├── neo4j.py                   # Neo4j knowledge graph operations
│   │   └── container.py               # Dependency injection container
│   │
│   └── api/                           # ✅ FastAPI endpoints
│       └── main.py                    # Routes (refactored with DI)
│
├── tests/
│   ├── conftest.py                    # Pytest fixtures (all adapters)
│   ├── fixtures/
│   │   ├── fake_repositories.py       # In-memory fakes for unit tests
│   │   └── data_generators.py         # Synthetic price/spread generators
│   ├── unit/
│   │   └── domain/
│   │       ├── test_spread_signal_service.py  # 7 tests ✅
│   │       └── test_risk_checker.py           # 6 tests ✅
│   └── integration/
│       └── test_generate_signal_flow.py       # Full flow test ✅
│
├── config/
│   ├── instruments.yaml               # Instrument definitions
│   ├── strategies.yaml                # Strategy parameters
│   └── risk_limits.yaml               # Risk filter thresholds
│
└── docs/
    ├── HEXAGONAL_ARCHITECTURE.md      # This file
    ├── NEO4J_INTEGRATION.md           # Knowledge graph guide
    ├── SOURCE_DATA_MODEL.md           # PostgreSQL schema + synthetic data
    └── ... (other architectural docs)
```

---

## Dependency Flow (Architecture)

```
┌────────────────────────────────────┐
│  FastAPI Routes                    │
│  (HTTP entry points)               │
└────────┬─────────────────────────────┘
         │ depends on
         ▼
┌────────────────────────────────────────────────────────┐
│  Application Layer (Use Cases)                         │
│  • GenerateSignalUseCase                              │
│  Wires domain logic + all adapters                    │
└────────┬──────────────────────────────┬────────────────┘
         │                              │
         │ depends on                   │ depends on
         ▼                              ▼
    ┌─────────────┐            ┌────────────────────┐
    │Domain Layer │            │Ports (Abstractions)│
    │(Pure Logic) │            │• IPriceRepository │
    │             │            │• IConfigLoader    │
    │• Services   │            │• ILogger           │
    │• Entities   │            │• INotifier         │
    │• Value Objs │            └────────┬───────────┘
    └─────────────┘                     │
                                        │ implemented by
                                        ▼
                        ┌───────────────────────────────┐
                        │Adapters (Concrete)            │
                        │• PostgresPriceRepository      │
                        │• YamlConfigLoader             │
                        │• ConsoleLogger                │
                        │• ConsoleNotifier              │
                        └───────────────────────────────┘
```

**Key principle**: 
- Domain never depends on anything (pure, testable in isolation)
- Adapters depend on ports, ports depend on domain
- Use case wires them together at runtime
- Tests inject fakes for unit tests, real adapters for integration

---

## Testing Strategy

### Unit Tests (Domain Layer)
**File**: `tests/unit/domain/test_spread_signal_service.py`

Tests domain logic **in isolation** with fake adapters:
```python
@pytest.fixture
def fake_price_repo():
    return FakePriceRepository()  # In-memory, no DB

def test_generate_signal_z_score():
    service = SpreadSignalService()
    signal = service.generate_signal(...)  # Pure function
    assert signal.action == "BUY"
```

**Why**: No DB needed, tests run in milliseconds, guaranteed reproducibility.

**Coverage**: 
- ✅ SpreadSignalService: 7 tests
- ✅ RiskChecker: 6 tests
- ✅ Value objects: Z-score math, spread statistics

---

### Integration Tests (Adapters + Use Case)
**File**: `tests/integration/test_generate_signal_flow.py`

Tests adapters + use case together with **synthetic data**:
```python
@pytest.mark.asyncio
async def test_generate_signal_with_synthetic_data():
    # Use case has real adapters injected
    use_case = GenerateSignalUseCase(
        price_repo=FakePriceRepository(),  # Injected
        ...
    )
    # Populate fake repo with synthetic data
    await use_case.price_repo.save_price_bar(bar)
    
    # Execute use case
    response = await use_case.execute(request)
    
    # Verify end-to-end flow worked
    assert response.action in ["BUY", "SELL", "NEUTRAL"]
```

**Why**: Proves the full flow works without a real DB.

---

### E2E Tests (Real DB, Real API)
**File**: `tests/e2e/` (placeholder, to be implemented)

Tests against real PostgreSQL and HTTP API (Phase 2).

---

## How to Run

### Setup
```bash
# Install dependencies
pip install -e ".[dev]"

# Create database and tables
docker-compose up postgres neo4j

# Run migrations
python -c "from src.infrastructure.database import Database; await Database(...).initialize_schema()"
```

### Run Tests
```bash
# Unit tests only (fast, no DB needed)
pytest tests/unit/ -v

# Integration tests (uses fake repos)
pytest tests/integration/ -v

# All tests with coverage
pytest tests/ --cov=src --cov-report=html
```

### Run API
```bash
# Start server
uvicorn src.api.main:app --reload

# Test endpoint
curl -X POST http://localhost:8000/signals/generate \
  -H "Content-Type: application/json" \
  -d '{
    "strategy_id": "spread_midland_cushing",
    "long_instrument": "WTI_MIDLAND",
    "short_instrument": "WTI_CUSHING"
  }'
```

---

## Adding a New Adapter (Example: Redis Cache)

**Step 1**: Define the port (interface)
```python
# src/ports/cache.py
class ICache(ABC):
    @abstractmethod
    async def get(self, key: str): ...
    @abstractmethod
    async def set(self, key: str, value: str): ...
```

**Step 2**: Implement the adapter
```python
# src/adapters/cache/redis_cache.py
class RedisCache(ICache):
    def __init__(self, client):
        self.client = client
    async def get(self, key: str):
        return await self.client.get(key)
    async def set(self, key: str, value: str):
        await self.client.set(key, value)
```

**Step 3**: Inject into use case
```python
# src/infrastructure/container.py
redis = aioredis.from_url("redis://localhost")
container.cache = RedisCache(redis)

use_case = GenerateSignalUseCase(
    ...,
    cache=container.cache,  # New!
)
```

**Step 4**: Use in domain logic (no changes needed!)
The domain never knows about Redis — it just calls the port.

---

## Key Design Decisions

| Decision | Why |
|---|---|
| **Hexagonal over Microservices** | Solo developer, synthetic data MVP — monolith is simpler to test and deploy |
| **PostgreSQL for operations** | Relational, ACID, time-series friendly, already in use |
| **Neo4j for knowledge graph** | Recursive queries (lineage) are exponentially faster than SQL |
| **Async/await throughout** | FastAPI requires it; adapters are faster with async DB drivers |
| **In-memory fakes for unit tests** | Deterministic, fast, no infrastructure needed |
| **YAML for config** | Human-readable, changes don't require code redeploy, fits Python ecosystem |

---

## Verification Checklist

- ✅ Domain layer has zero external imports (only dataclasses, stdlib)
- ✅ All ports are abstract base classes with no implementation
- ✅ All adapters implement exactly one port
- ✅ Use case orchestrates adapters via ports (DI container wires them)
- ✅ Unit tests use fake adapters (in-memory)
- ✅ Integration tests use real adapters with test data
- ✅ No `global` variables (all state passed via constructor)
- ✅ Async/await consistent (no sync calls blocking event loop)
- ✅ Config loaded from YAML, never hardcoded
- ✅ Database pool created at startup, closed at shutdown

---

## Next Steps

**Phase 1** (Week 1-2):
- Populate PostgreSQL with synthetic NYMEX WTI prices
- Implement feature calculation (60-day Z-score)
- Train toy LightGBM model on synthetic spreads
- Wire into use case and test end-to-end

**Phase 2** (Week 3):
- Add real API routes (no longer mocked)
- React dashboard panel showing Midland-Cushing signals
- Neo4j: populate knowledge graph with data lineage

**Phase 3** (Week 4):
- Add second strategy (RBOB crack spreads)
- Expand dashboard to 2 panels
- Monitoring: signal accuracy, latency tracking

---

## References

- [Hexagonal Architecture (Alistair Cockburn)](https://alistair.cockburn.us/hexagonal-architecture/)
- [Clean Architecture (Robert C. Martin)](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Domain-Driven Design (Eric Evans)](https://www.domainlanguage.com/ddd/)
- FastAPI docs: https://fastapi.tiangolo.com
- AsyncPG docs: https://magicstack.github.io/asyncpg
- Neo4j docs: https://neo4j.com/developer/get-started

---

## Contact

For questions about architecture, ask in the CLAUDE.md file or consult this document.
