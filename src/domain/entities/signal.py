"""Signal entity."""
from dataclasses import dataclass
from datetime import datetime
from typing import Literal


@dataclass
class Signal:
    """A trading signal."""

    strategy_id: str
    instrument_long: str
    instrument_short: str
    action: Literal["BUY", "SELL", "NEUTRAL"]
    confidence: float
    timestamp: datetime
    rationale: str
    expected_hold_days: int = 3

    def __post_init__(self):
        """Validate signal."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be 0.0-1.0, got {self.confidence}")
        if self.expected_hold_days <= 0:
            raise ValueError("Expected hold days must be positive")
