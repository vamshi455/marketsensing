"""Z-score value object and calculation logic."""
from dataclasses import dataclass


@dataclass(frozen=True)
class ZScore:
    """Immutable Z-score result."""

    value: float
    threshold: float

    @property
    def is_entry_signal(self) -> bool:
        """True if |z_score| >= threshold."""
        return abs(self.value) >= self.threshold

    @property
    def is_buy(self) -> bool:
        """True if z_score is strongly negative (wide spread)."""
        return self.value < -self.threshold

    @property
    def is_sell(self) -> bool:
        """True if z_score is strongly positive (tight spread)."""
        return self.value > self.threshold
