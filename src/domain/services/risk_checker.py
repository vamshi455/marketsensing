"""Risk checker service: apply position and correlation limits."""
from dataclasses import dataclass
from typing import Optional

from src.domain.entities.signal import Signal
from src.domain.exceptions import RiskLimitExceededError


@dataclass
class RiskLimits:
    """Risk limit thresholds."""

    max_position_size: int  # contracts
    max_daily_loss: float  # dollars
    max_correlation_to_existing: float  # 0.0-1.0
    min_confidence_threshold: float  # 0.0-1.0


class RiskChecker:
    """Apply risk filters to signals."""

    def __init__(self, limits: RiskLimits):
        self.limits = limits

    def check_confidence(self, signal: Signal) -> bool:
        """Check if signal meets minimum confidence threshold."""
        return signal.confidence >= self.limits.min_confidence_threshold

    def check_position_size(self, current_position_size: int, proposed_size: int) -> bool:
        """Check if position size would exceed limit."""
        total = current_position_size + proposed_size
        return total <= self.limits.max_position_size

    def check_signal(
        self,
        signal: Signal,
        current_position_size: int = 0,
        proposed_size: int = 1,
        correlation_to_existing: Optional[float] = None,
    ) -> tuple[bool, str]:
        """
        Check if signal passes all risk filters.

        Returns:
            (passes: bool, reason: str)
        """
        if not self.check_confidence(signal):
            return (
                False,
                f"Confidence {signal.confidence:.2f} below threshold {self.limits.min_confidence_threshold}",
            )

        if not self.check_position_size(current_position_size, proposed_size):
            return (
                False,
                f"Position size {current_position_size + proposed_size} exceeds limit {self.limits.max_position_size}",
            )

        if (
            correlation_to_existing is not None
            and correlation_to_existing > self.limits.max_correlation_to_existing
        ):
            return (
                False,
                f"Correlation {correlation_to_existing:.2f} exceeds limit {self.limits.max_correlation_to_existing}",
            )

        return True, "All risk checks passed"
