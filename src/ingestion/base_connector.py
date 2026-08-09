"""
Base connector class for all data sources.

All data source connectors (EIA, Kpler, TickerTech, etc.) inherit from this
to ensure consistent error handling, retry logic, and logging.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional

import structlog

logger = structlog.get_logger()


class BaseConnector(ABC):
    """Abstract base class for all data connectors."""

    def __init__(self, name: str, config: Dict[str, Any]):
        """
        Initialize connector.

        Args:
            name: Connector identifier (e.g., 'kpler', 'eia', 'weather')
            config: Configuration dict (API keys, endpoints, etc.)
        """
        self.name = name
        self.config = config
        self.last_fetch_time: Optional[datetime] = None

    @abstractmethod
    async def fetch(self) -> List[Dict[str, Any]]:
        """
        Fetch data from source.

        Returns:
            List of data records (dict format)

        Raises:
            ConnectorError: If fetch fails
        """
        pass

    @abstractmethod
    def validate(self, record: Dict[str, Any]) -> bool:
        """
        Validate a single record against schema.

        Args:
            record: Data record to validate

        Returns:
            True if valid, False otherwise
        """
        pass

    async def fetch_with_retry(self, max_retries: int = 3) -> List[Dict[str, Any]]:
        """
        Fetch data with exponential backoff retry.

        Args:
            max_retries: Maximum retry attempts

        Returns:
            List of validated data records
        """
        import asyncio

        for attempt in range(max_retries):
            try:
                data = await self.fetch()
                validated_data = [r for r in data if self.validate(r)]
                self.last_fetch_time = datetime.utcnow()
                logger.info(
                    "fetch_success",
                    connector=self.name,
                    records_fetched=len(data),
                    records_valid=len(validated_data),
                )
                return validated_data
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(
                        "fetch_failed_max_retries",
                        connector=self.name,
                        error=str(e),
                    )
                    raise
                wait_time = 2 ** attempt
                logger.warning(
                    "fetch_retry",
                    connector=self.name,
                    attempt=attempt + 1,
                    wait_seconds=wait_time,
                    error=str(e),
                )
                await asyncio.sleep(wait_time)

    def get_freshness_minutes(self) -> Optional[int]:
        """Get minutes elapsed since last fetch."""
        if self.last_fetch_time is None:
            return None
        delta = datetime.utcnow() - self.last_fetch_time
        return int(delta.total_seconds() / 60)
