"""Fake (in-memory) implementations of repositories for testing."""
from datetime import datetime
from typing import Dict, List, Optional

from src.domain.entities.price_bar import PriceBar
from src.domain.entities.signal import Signal
from src.domain.entities.spread import Spread
from src.ports.repository import IPriceRepository, ISignalRepository, ISpreadRepository


class FakePriceRepository(IPriceRepository):
    """In-memory price repository for testing."""

    def __init__(self):
        """Initialize with empty storage."""
        self.storage: Dict[str, List[PriceBar]] = {}

    async def get_price_bars(
        self,
        instrument: str,
        start: datetime,
        end: datetime,
    ) -> List[PriceBar]:
        """Return price bars in date range."""
        if instrument not in self.storage:
            return []
        return [
            bar
            for bar in self.storage[instrument]
            if start <= bar.timestamp <= end
        ]

    async def get_latest_price(self, instrument: str) -> Optional[PriceBar]:
        """Return latest price bar."""
        if instrument not in self.storage or not self.storage[instrument]:
            return None
        return self.storage[instrument][-1]

    async def save_price_bar(self, bar: PriceBar) -> None:
        """Save a price bar."""
        if bar.instrument not in self.storage:
            self.storage[bar.instrument] = []
        self.storage[bar.instrument].append(bar)
        self.storage[bar.instrument].sort(key=lambda x: x.timestamp)


class FakeSpreadRepository(ISpreadRepository):
    """In-memory spread repository for testing."""

    def __init__(self):
        """Initialize with empty storage."""
        self.storage: List[Spread] = []

    async def get_spread(
        self,
        long_instrument: str,
        short_instrument: str,
        timestamp: datetime,
    ) -> Optional[Spread]:
        """Return spread at specific timestamp."""
        for spread in self.storage:
            if (
                spread.long_instrument == long_instrument
                and spread.short_instrument == short_instrument
                and spread.timestamp == timestamp
            ):
                return spread
        return None

    async def get_latest_spread(
        self,
        long_instrument: str,
        short_instrument: str,
    ) -> Optional[Spread]:
        """Return latest spread."""
        matching = [
            s
            for s in self.storage
            if s.long_instrument == long_instrument
            and s.short_instrument == short_instrument
        ]
        return max(matching, key=lambda x: x.timestamp) if matching else None

    async def save_spread(self, spread: Spread) -> None:
        """Save a spread."""
        self.storage.append(spread)
        self.storage.sort(key=lambda x: x.timestamp)


class FakeSignalRepository(ISignalRepository):
    """In-memory signal repository for testing."""

    def __init__(self):
        """Initialize with empty storage."""
        self.storage: Dict[str, Signal] = {}

    async def save_signal(self, signal: Signal) -> str:
        """Save a signal."""
        from uuid import uuid4

        signal_id = str(uuid4())
        self.storage[signal_id] = signal
        return signal_id

    async def get_latest_signals(self, limit: int = 10) -> List[Signal]:
        """Return latest signals."""
        signals = list(self.storage.values())
        signals.sort(key=lambda x: x.timestamp, reverse=True)
        return signals[:limit]

    async def get_signals_by_strategy(self, strategy_id: str, limit: int = 10) -> List[Signal]:
        """Return signals for a strategy."""
        signals = [
            s
            for s in self.storage.values()
            if s.strategy_id == strategy_id
        ]
        signals.sort(key=lambda x: x.timestamp, reverse=True)
        return signals[:limit]
