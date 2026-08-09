"""YAML configuration loader adapter."""
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from src.ports.config import IConfigLoader


class YamlConfigLoader(IConfigLoader):
    """Load configuration from YAML files."""

    def __init__(self, config_dir: str = "config"):
        """Initialize with configuration directory."""
        self.config_dir = Path(config_dir)
        self._cache: Dict[str, Any] = {}

    def load_strategy(self, strategy_id: str) -> Dict[str, Any]:
        """Load strategy configuration."""
        strategies = self._load_file("strategies.yaml")
        if strategy_id not in strategies.get("strategies", {}):
            raise ValueError(f"Strategy {strategy_id} not found")
        return strategies["strategies"][strategy_id]

    def load_instrument(self, instrument_code: str) -> Dict[str, Any]:
        """Load instrument configuration."""
        instruments = self._load_file("instruments.yaml")
        if instrument_code not in instruments.get("instruments", {}):
            raise ValueError(f"Instrument {instrument_code} not found")
        return instruments["instruments"][instrument_code]

    def load_risk_limits(self) -> Dict[str, Any]:
        """Load risk limits configuration."""
        return self._load_file("risk_limits.yaml")

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """Get a configuration value by dot-notation key."""
        parts = key.split(".")
        for part in parts:
            # Try loading from file if root key
            if not self._cache or part not in str(self._cache):
                try:
                    data = self._load_file(f"{part}.yaml")
                    return data.get(key, default)
                except FileNotFoundError:
                    pass
        return default

    def _load_file(self, filename: str) -> Dict[str, Any]:
        """Load and cache YAML file."""
        if filename in self._cache:
            return self._cache[filename]

        filepath = self.config_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Config file not found: {filepath}")

        with open(filepath, "r") as f:
            data = yaml.safe_load(f) or {}
        self._cache[filename] = data
        return data
