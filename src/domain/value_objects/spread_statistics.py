"""Spread statistics value object."""
from dataclasses import dataclass
from typing import Optional

from src.domain.exceptions import InsufficientDataError
from src.domain.value_objects.z_score import ZScore


@dataclass(frozen=True)
class SpreadStatistics:
    """Immutable spread statistics (mean, std, quantiles)."""

    mean: float
    std: float
    median: Optional[float] = None
    p25: Optional[float] = None
    p75: Optional[float] = None

    def calculate_z_score(self, current_value: float) -> ZScore:
        """Calculate Z-score for current value."""
        if self.std == 0:
            raise InsufficientDataError("Cannot calculate Z-score with zero volatility")
        z = (current_value - self.mean) / self.std
        return ZScore(value=z, threshold=2.0)

    def to_dict(self) -> dict:
        """Export as dictionary."""
        return {
            "mean": self.mean,
            "std": self.std,
            "median": self.median,
            "p25": self.p25,
            "p75": self.p75,
        }
