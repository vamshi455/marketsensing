"""Logger ports (abstract logging)."""
from abc import ABC, abstractmethod
from typing import Any, Dict


class ILogger(ABC):
    """Abstract logger interface."""

    @abstractmethod
    def info(self, message: str, **context: Any) -> None:
        """Log info level."""

    @abstractmethod
    def error(self, message: str, **context: Any) -> None:
        """Log error level."""

    @abstractmethod
    def debug(self, message: str, **context: Any) -> None:
        """Log debug level."""

    @abstractmethod
    def warning(self, message: str, **context: Any) -> None:
        """Log warning level."""
