"""Synthetic data generators for testing."""
from datetime import datetime, timedelta

from src.domain.entities.price_bar import PriceBar
from src.domain.entities.spread import Spread


class SyntheticPriceGenerator:
    """Generate deterministic synthetic price bars."""

    def __init__(self, seed: int = 42):
        """Initialize with random seed for reproducibility."""
        import random
        self.random = random.Random(seed)

    def generate_price_bars(
        self,
        instrument: str,
        start: datetime,
        days: int,
        base_price: float = 80.0,
        volatility: float = 0.02,
    ) -> list[PriceBar]:
        """Generate deterministic price bars."""
        bars = []
        current_price = base_price
        current_date = start

        for _ in range(days):
            daily_return = self.random.gauss(0, volatility)
            close_price = current_price * (1 + daily_return)

            bar = PriceBar(
                instrument=instrument,
                timestamp=current_date,
                open=current_price,
                high=max(current_price, close_price) * 1.01,
                low=min(current_price, close_price) * 0.99,
                close=close_price,
                volume=self.random.randint(100_000, 1_000_000),
            )
            bars.append(bar)
            current_price = close_price
            current_date += timedelta(days=1)

        return bars


class SyntheticSpreadGenerator:
    """Generate deterministic synthetic spreads."""

    def __init__(self, seed: int = 42):
        """Initialize with random seed."""
        import random
        self.random = random.Random(seed)

    def generate_spreads(
        self,
        long_instrument: str,
        short_instrument: str,
        start: datetime,
        days: int,
        mean_spread: float = -1.0,
        spread_volatility: float = 0.5,
    ) -> list[Spread]:
        """Generate deterministic spreads."""
        spreads = []
        current_date = start

        for _ in range(days):
            spread_noise = self.random.gauss(0, spread_volatility)
            spread_value = mean_spread + spread_noise

            spread = Spread(
                long_instrument=long_instrument,
                short_instrument=short_instrument,
                value=spread_value,
                timestamp=current_date,
            )
            spreads.append(spread)
            current_date += timedelta(days=1)

        return spreads
