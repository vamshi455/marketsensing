"""Price bar entity (OHLCV)."""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class PriceBar:
    """A price bar with OHLCV (open, high, low, close, volume)."""

    instrument: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int

    def __post_init__(self):
        """Validate price bar consistency."""
        if not all(p >= 0 for p in [self.open, self.high, self.low, self.close]):
            raise ValueError("Prices cannot be negative")
        if not (self.low <= self.close <= self.high and self.low <= self.open <= self.high):
            raise ValueError("Price relationship violated: low <= close/open <= high")
        if self.volume < 0:
            raise ValueError("Volume cannot be negative")
