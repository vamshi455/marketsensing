"""Spread signal service: core trading logic."""
from datetime import datetime
from typing import Literal

from src.domain.entities.signal import Signal
from src.domain.exceptions import InsufficientDataError, InvalidSignalError
from src.domain.value_objects.spread_statistics import SpreadStatistics


class SpreadSignalService:
    """Pure business logic: convert spreads to signals via Z-score."""

    def generate_signal(
        self,
        strategy_id: str,
        long_instrument: str,
        short_instrument: str,
        current_spread: float,
        spread_stats: SpreadStatistics,
        z_score_threshold: float = 2.0,
        expected_hold_days: int = 3,
    ) -> Signal:
        """
        Generate a trading signal from spread and statistics.

        Args:
            strategy_id: Strategy identifier (e.g., "spread_midland_cushing")
            long_instrument: Long leg instrument
            short_instrument: Short leg instrument
            current_spread: Current spread value (cents)
            spread_stats: Statistics (mean, std) for Z-score calculation
            z_score_threshold: Entry threshold (default 2.0 sigma)
            expected_hold_days: Expected holding period

        Returns:
            Signal with action (BUY/SELL/NEUTRAL) and confidence

        Raises:
            InsufficientDataError: If std is zero
            InvalidSignalError: If parameters are invalid
        """
        if z_score_threshold <= 0:
            raise InvalidSignalError("Z-score threshold must be positive")

        if spread_stats.std == 0:
            return Signal(
                strategy_id=strategy_id,
                instrument_long=long_instrument,
                instrument_short=short_instrument,
                action="NEUTRAL",
                confidence=0.0,
                timestamp=datetime.utcnow(),
                rationale="Insufficient volatility to generate signal",
                expected_hold_days=expected_hold_days,
            )

        z_score = (current_spread - spread_stats.mean) / spread_stats.std

        if z_score < -z_score_threshold:
            confidence = min(abs(z_score) / 3.0, 1.0)
            return Signal(
                strategy_id=strategy_id,
                instrument_long=long_instrument,
                instrument_short=short_instrument,
                action="BUY",
                confidence=confidence,
                timestamp=datetime.utcnow(),
                rationale=f"Spread at {z_score:.2f}σ below mean ({spread_stats.mean:.2f}); wide spread entry",
                expected_hold_days=expected_hold_days,
            )

        elif z_score > z_score_threshold:
            confidence = min(abs(z_score) / 3.0, 1.0)
            return Signal(
                strategy_id=strategy_id,
                instrument_long=long_instrument,
                instrument_short=short_instrument,
                action="SELL",
                confidence=confidence,
                timestamp=datetime.utcnow(),
                rationale=f"Spread at {z_score:.2f}σ above mean ({spread_stats.mean:.2f}); tight spread entry",
                expected_hold_days=expected_hold_days,
            )

        else:
            return Signal(
                strategy_id=strategy_id,
                instrument_long=long_instrument,
                instrument_short=short_instrument,
                action="NEUTRAL",
                confidence=0.0,
                timestamp=datetime.utcnow(),
                rationale=f"Spread at {z_score:.2f}σ within bands",
                expected_hold_days=expected_hold_days,
            )
