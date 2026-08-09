"""Console logger adapter."""
import json
from typing import Any

from src.ports.logger import ILogger


class ConsoleLogger(ILogger):
    """Simple console logger for development."""

    def info(self, message: str, **context: Any) -> None:
        """Log info level."""
        print(json.dumps({"level": "INFO", "message": message, **context}))

    def error(self, message: str, **context: Any) -> None:
        """Log error level."""
        print(json.dumps({"level": "ERROR", "message": message, **context}))

    def debug(self, message: str, **context: Any) -> None:
        """Log debug level."""
        print(json.dumps({"level": "DEBUG", "message": message, **context}))

    def warning(self, message: str, **context: Any) -> None:
        """Log warning level."""
        print(json.dumps({"level": "WARNING", "message": message, **context}))
