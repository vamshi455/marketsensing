"""Instrument value object."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Instrument:
    """Immutable instrument identifier."""

    code: str
    commodity: str  # e.g., "WTI", "RBOB", "ULSD"
    contract_month: str = ""  # e.g., "202609" for Sep 2026

    def __post_init__(self):
        """Validate instrument."""
        if not self.code:
            raise ValueError("Instrument code cannot be empty")
        if not self.commodity:
            raise ValueError("Commodity cannot be empty")
