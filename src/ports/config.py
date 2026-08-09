"""Configuration ports (abstract config loading)."""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class IConfigLoader(ABC):
    """Abstract configuration loader."""

    @abstractmethod
    def load_strategy(self, strategy_id: str) -> Dict[str, Any]:
        """Load strategy configuration."""

    @abstractmethod
    def load_instrument(self, instrument_code: str) -> Dict[str, Any]:
        """Load instrument configuration."""

    @abstractmethod
    def load_risk_limits(self) -> Dict[str, Any]:
        """Load risk limits configuration."""

    @abstractmethod
    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """Get a configuration value by key."""
