"""PostgreSQL price repository adapter."""
from datetime import datetime
from typing import List, Optional

from src.domain.entities.price_bar import PriceBar
from src.ports.repository import IPriceRepository


class PostgresPriceRepository(IPriceRepository):
    """Concrete PostgreSQL price repository."""

    def __init__(self, db_pool):
        """Initialize with database connection pool."""
        self.db_pool = db_pool

    async def get_price_bars(
        self,
        instrument: str,
        start: datetime,
        end: datetime,
    ) -> List[PriceBar]:
        """Fetch price bars from PostgreSQL."""
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT instrument, timestamp, open, high, low, close, volume
                FROM price_bars
                WHERE instrument = $1 AND timestamp BETWEEN $2 AND $3
                ORDER BY timestamp ASC
                """,
                instrument,
                start,
                end,
            )
            return [
                PriceBar(
                    instrument=row["instrument"],
                    timestamp=row["timestamp"],
                    open=row["open"],
                    high=row["high"],
                    low=row["low"],
                    close=row["close"],
                    volume=row["volume"],
                )
                for row in rows
            ]

    async def get_latest_price(self, instrument: str) -> Optional[PriceBar]:
        """Fetch the latest price bar."""
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT instrument, timestamp, open, high, low, close, volume
                FROM price_bars
                WHERE instrument = $1
                ORDER BY timestamp DESC
                LIMIT 1
                """,
                instrument,
            )
            if row is None:
                return None
            return PriceBar(
                instrument=row["instrument"],
                timestamp=row["timestamp"],
                open=row["open"],
                high=row["high"],
                low=row["low"],
                close=row["close"],
                volume=row["volume"],
            )

    async def save_price_bar(self, bar: PriceBar) -> None:
        """Save a price bar."""
        async with self.db_pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO price_bars (instrument, timestamp, open, high, low, close, volume)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (instrument, timestamp) DO UPDATE SET
                    open = EXCLUDED.open,
                    high = EXCLUDED.high,
                    low = EXCLUDED.low,
                    close = EXCLUDED.close,
                    volume = EXCLUDED.volume
                """,
                bar.instrument,
                bar.timestamp,
                bar.open,
                bar.high,
                bar.low,
                bar.close,
                bar.volume,
            )
