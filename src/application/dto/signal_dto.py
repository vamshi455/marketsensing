"""Signal DTOs."""
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Literal


@dataclass
class GenerateSignalRequest:
    """Request to generate a signal."""

    strategy_id: str
    long_instrument: str
    short_instrument: str
    z_score_threshold: float = 2.0
    expected_hold_days: int = 3


@dataclass
class GenerateSignalResponse:
    """Response from signal generation."""

    strategy_id: str
    instrument_long: str
    instrument_short: str
    action: Literal["BUY", "SELL", "NEUTRAL"]
    confidence: float
    rationale: str
    timestamp: datetime

    def to_dict(self):
        """Convert to dictionary."""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data
