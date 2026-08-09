"""Integration test: full signal generation flow with fake adapters."""
import pytest
from datetime import datetime

from src.application.dto.signal_dto import GenerateSignalRequest
from src.domain.entities.price_bar import PriceBar
from tests.fixtures.data_generators import SyntheticPriceGenerator, SyntheticSpreadGenerator


@pytest.mark.asyncio
async def test_generate_signal_with_synthetic_data(generate_signal_use_case, fake_price_repo):
    """Test full signal generation with synthetic price data."""
    # Setup: inject synthetic data into fake repository
    generator = SyntheticPriceGenerator(seed=42)
    start = datetime(2026, 1, 1)

    # Generate prices for both instruments
    midland_prices = generator.generate_price_bars(
        "WTI_MIDLAND", start, days=60, base_price=75.0
    )
    cushing_prices = generator.generate_price_bars(
        "WTI_CUSHING", start, days=60, base_price=73.0
    )

    # Save to fake repository
    for bar in midland_prices:
        await fake_price_repo.save_price_bar(bar)
    for bar in cushing_prices:
        await fake_price_repo.save_price_bar(bar)

    # Execute: generate signal
    request = GenerateSignalRequest(
        strategy_id="spread_midland_cushing",
        long_instrument="WTI_MIDLAND",
        short_instrument="WTI_CUSHING",
        z_score_threshold=2.0,
    )

    response = await generate_signal_use_case.execute(request)

    # Assert: response is valid
    assert response.strategy_id == "spread_midland_cushing"
    assert response.instrument_long == "WTI_MIDLAND"
    assert response.instrument_short == "WTI_CUSHING"
    assert response.action in ["BUY", "SELL", "NEUTRAL"]
    assert 0.0 <= response.confidence <= 1.0
    assert response.timestamp is not None

    # Assert: signal was persisted
    signals = await generate_signal_use_case.signal_repo.get_latest_signals(limit=1)
    assert len(signals) > 0
    assert signals[0].strategy_id == "spread_midland_cushing"
