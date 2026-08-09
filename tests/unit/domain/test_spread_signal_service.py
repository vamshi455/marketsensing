"""Unit tests for SpreadSignalService (pure domain logic)."""
import pytest

from src.domain.services.spread_signal_service import SpreadSignalService
from src.domain.value_objects.spread_statistics import SpreadStatistics


@pytest.fixture
def service():
    """Create service instance."""
    return SpreadSignalService()


class TestSpreadSignalService:
    """Test pure signal logic without adapters or I/O."""

    def test_buy_signal_when_spread_wide(self, service):
        """Spread 2+ std devs below mean → BUY."""
        signal = service.generate_signal(
            strategy_id="spread_midland_cushing",
            long_instrument="WTI_MIDLAND",
            short_instrument="WTI_CUSHING",
            current_spread=-3.0,  # Wide spread
            spread_stats=SpreadStatistics(mean=-1.0, std=1.0),
            z_score_threshold=2.0,
        )
        assert signal.action == "BUY"
        assert signal.confidence > 0.5
        assert "2.00σ below" in signal.rationale

    def test_sell_signal_when_spread_tight(self, service):
        """Spread 2+ std devs above mean → SELL."""
        signal = service.generate_signal(
            strategy_id="spread_midland_cushing",
            long_instrument="WTI_MIDLAND",
            short_instrument="WTI_CUSHING",
            current_spread=1.0,  # Tight spread
            spread_stats=SpreadStatistics(mean=-1.0, std=1.0),
            z_score_threshold=2.0,
        )
        assert signal.action == "SELL"
        assert signal.confidence > 0.5
        assert "2.00σ above" in signal.rationale

    def test_neutral_signal_within_bands(self, service):
        """Spread within ±2σ → NEUTRAL."""
        signal = service.generate_signal(
            strategy_id="spread_midland_cushing",
            long_instrument="WTI_MIDLAND",
            short_instrument="WTI_CUSHING",
            current_spread=-0.5,
            spread_stats=SpreadStatistics(mean=-1.0, std=1.0),
            z_score_threshold=2.0,
        )
        assert signal.action == "NEUTRAL"
        assert signal.confidence == 0.0

    def test_zero_volatility_returns_neutral(self, service):
        """When std=0, return NEUTRAL (can't calculate z-score)."""
        signal = service.generate_signal(
            strategy_id="spread_midland_cushing",
            long_instrument="WTI_MIDLAND",
            short_instrument="WTI_CUSHING",
            current_spread=0.0,
            spread_stats=SpreadStatistics(mean=0.0, std=0.0),
        )
        assert signal.action == "NEUTRAL"
        assert "Insufficient volatility" in signal.rationale

    def test_confidence_increases_with_sigma(self, service):
        """Confidence should increase as signal gets stronger."""
        signal_3sigma = service.generate_signal(
            strategy_id="spread_midland_cushing",
            long_instrument="WTI_MIDLAND",
            short_instrument="WTI_CUSHING",
            current_spread=-4.0,
            spread_stats=SpreadStatistics(mean=-1.0, std=1.0),
        )
        signal_2point5sigma = service.generate_signal(
            strategy_id="spread_midland_cushing",
            long_instrument="WTI_MIDLAND",
            short_instrument="WTI_CUSHING",
            current_spread=-3.5,
            spread_stats=SpreadStatistics(mean=-1.0, std=1.0),
        )
        assert signal_3sigma.confidence > signal_2point5sigma.confidence

    def test_invalid_z_score_threshold_raises_error(self, service):
        """Zero or negative threshold should raise error."""
        with pytest.raises(ValueError):
            service.generate_signal(
                strategy_id="spread_midland_cushing",
                long_instrument="WTI_MIDLAND",
                short_instrument="WTI_CUSHING",
                current_spread=0.0,
                spread_stats=SpreadStatistics(mean=0.0, std=1.0),
                z_score_threshold=0.0,
            )

    def test_signal_confidence_capped_at_one(self, service):
        """Confidence should never exceed 1.0."""
        signal = service.generate_signal(
            strategy_id="spread_midland_cushing",
            long_instrument="WTI_MIDLAND",
            short_instrument="WTI_CUSHING",
            current_spread=-10.0,  # Very far from mean
            spread_stats=SpreadStatistics(mean=-1.0, std=1.0),
        )
        assert signal.confidence <= 1.0
