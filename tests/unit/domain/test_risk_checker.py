"""Unit tests for RiskChecker service."""
import pytest
from datetime import datetime

from src.domain.entities.signal import Signal
from src.domain.services.risk_checker import RiskChecker, RiskLimits


@pytest.fixture
def risk_limits():
    """Create risk limits."""
    return RiskLimits(
        max_position_size=100,
        max_daily_loss=10_000.0,
        max_correlation_to_existing=0.8,
        min_confidence_threshold=0.3,
    )


@pytest.fixture
def risk_checker(risk_limits):
    """Create risk checker."""
    return RiskChecker(risk_limits)


class TestRiskChecker:
    """Test risk filtering logic."""

    def test_signal_passes_confidence_check(self, risk_checker):
        """Signal above threshold passes confidence check."""
        signal = Signal(
            strategy_id="test",
            instrument_long="A",
            instrument_short="B",
            action="BUY",
            confidence=0.5,
            timestamp=datetime.utcnow(),
            rationale="Test",
        )
        assert risk_checker.check_confidence(signal)

    def test_signal_fails_confidence_check(self, risk_checker):
        """Signal below threshold fails confidence check."""
        signal = Signal(
            strategy_id="test",
            instrument_long="A",
            instrument_short="B",
            action="BUY",
            confidence=0.2,
            timestamp=datetime.utcnow(),
            rationale="Test",
        )
        assert not risk_checker.check_confidence(signal)

    def test_position_size_within_limit(self, risk_checker):
        """Position size within limit passes."""
        assert risk_checker.check_position_size(current_position_size=50, proposed_size=30)

    def test_position_size_exceeds_limit(self, risk_checker):
        """Position size exceeding limit fails."""
        assert not risk_checker.check_position_size(
            current_position_size=80, proposed_size=30
        )

    def test_full_check_passes_all_filters(self, risk_checker):
        """Signal passing all checks returns True."""
        signal = Signal(
            strategy_id="test",
            instrument_long="A",
            instrument_short="B",
            action="BUY",
            confidence=0.7,
            timestamp=datetime.utcnow(),
            rationale="Test",
        )
        passes, reason = risk_checker.check_signal(
            signal,
            current_position_size=0,
            proposed_size=10,
            correlation_to_existing=0.5,
        )
        assert passes
        assert "All risk checks passed" in reason

    def test_full_check_fails_on_confidence(self, risk_checker):
        """Signal failing confidence check returns False."""
        signal = Signal(
            strategy_id="test",
            instrument_long="A",
            instrument_short="B",
            action="BUY",
            confidence=0.1,
            timestamp=datetime.utcnow(),
            rationale="Test",
        )
        passes, reason = risk_checker.check_signal(signal)
        assert not passes
        assert "Confidence" in reason
