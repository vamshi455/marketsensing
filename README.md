# MarketSensing

Oil & Gas Market Sensing and Trading Signal Platform for US-focused crude, products, and natural gas markets.

## Quick Start

```bash
# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Start API server (development)
uvicorn src.api.main:app --reload
```

## Project Structure

See [CLAUDE.md](CLAUDE.md) for full architecture and module documentation.

## Phases

- **Phase 1**: WTI location spreads + time spreads (simple rules)
- **Phase 2**: Crack spreads + regime detection (ML)
- **Phase 3**: Natural gas + execution layer design
