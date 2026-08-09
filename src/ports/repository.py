"""Repository ports (abstract data access)."""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from src.domain.entities.price_bar import PriceBar
from src.domain.entities.signal import Signal
from src.domain.entities.spread import Spread


class IPriceRepository(ABC):
    """Abstract price data repository."""

    @abstractmethod
    async def get_price_bars(
        self,
        instrument: str,
        start: datetime,
        end: datetime,
    ) -> List[PriceBar]:
        """Fetch price bars for an instrument in a time range."""

    @abstractmethod
    async def get_latest_price(self, instrument: str) -> Optional[PriceBar]:
        """Fetch the latest price bar for an instrument."""

    @abstractmethod
    async def save_price_bar(self, bar: PriceBar) -> None:
        """Save a price bar."""


class ISpreadRepository(ABC):
    """Abstract spread data repository."""

    @abstractmethod
    async def get_spread(
        self,
        long_instrument: str,
        short_instrument: str,
        timestamp: datetime,
    ) -> Optional[Spread]:
        """Fetch spread at a specific timestamp."""

    @abstractmethod
    async def get_latest_spread(
        self,
        long_instrument: str,
        short_instrument: str,
    ) -> Optional[Spread]:
        """Fetch the latest spread for an instrument pair."""

    @abstractmethod
    async def save_spread(self, spread: Spread) -> None:
        """Save a spread."""


class ISignalRepository(ABC):
    """Abstract signal storage repository."""

    @abstractmethod
    async def save_signal(self, signal: Signal) -> str:
        """Save a signal, return signal_id."""

    @abstractmethod
    async def get_latest_signals(self, limit: int = 10) -> List[Signal]:
        """Fetch the most recent signals."""

    @abstractmethod
    async def get_signals_by_strategy(self, strategy_id: str, limit: int = 10) -> List[Signal]:
        """Fetch signals for a strategy."""
