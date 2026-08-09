"""Notifier ports (abstract signal broadcasting)."""
from abc import ABC, abstractmethod

from src.domain.entities.signal import Signal


class INotifier(ABC):
    """Abstract signal notifier."""

    @abstractmethod
    async def notify_signal(self, signal: Signal) -> None:
        """Broadcast a signal to subscribers."""

    @abstractmethod
    async def notify_error(self, error_message: str) -> None:
        """Broadcast an error message."""
