"""Spread entity."""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Spread:
    """A price spread between two instruments."""

    long_instrument: str
    short_instrument: str
    value: float
    timestamp: datetime

    def __post_init__(self):
        """Validate spread."""
        if self.value is None:
            raise ValueError("Spread value cannot be None")
        if self.long_instrument == self.short_instrument:
            raise ValueError("Cannot spread same instrument against itself")
