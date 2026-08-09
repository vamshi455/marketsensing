"""PostgreSQL spread repository adapter."""
from datetime import datetime
from typing import Optional

from src.domain.entities.spread import Spread
from src.ports.repository import ISpreadRepository


class PostgresSpreadRepository(ISpreadRepository):
    """Concrete PostgreSQL spread repository."""

    def __init__(self, db_pool):
        """Initialize with database connection pool."""
        self.db_pool = db_pool

    async def get_spread(
        self,
        long_instrument: str,
        short_instrument: str,
        timestamp: datetime,
    ) -> Optional[Spread]:
        """Fetch spread at a specific timestamp."""
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT long_instrument, short_instrument, value, timestamp
                FROM spreads
                WHERE long_instrument = $1 AND short_instrument = $2 AND timestamp = $3
                """,
                long_instrument,
                short_instrument,
                timestamp,
            )
            if row is None:
                return None
            return Spread(
                long_instrument=row["long_instrument"],
                short_instrument=row["short_instrument"],
                value=row["value"],
                timestamp=row["timestamp"],
            )

    async def get_latest_spread(
        self,
        long_instrument: str,
        short_instrument: str,
    ) -> Optional[Spread]:
        """Fetch the latest spread."""
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT long_instrument, short_instrument, value, timestamp
                FROM spreads
                WHERE long_instrument = $1 AND short_instrument = $2
                ORDER BY timestamp DESC
                LIMIT 1
                """,
                long_instrument,
                short_instrument,
            )
            if row is None:
                return None
            return Spread(
                long_instrument=row["long_instrument"],
                short_instrument=row["short_instrument"],
                value=row["value"],
                timestamp=row["timestamp"],
            )

    async def save_spread(self, spread: Spread) -> None:
        """Save a spread."""
        async with self.db_pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO spreads (long_instrument, short_instrument, value, timestamp)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (long_instrument, short_instrument, timestamp) DO UPDATE SET
                    value = EXCLUDED.value
                """,
                spread.long_instrument,
                spread.short_instrument,
                spread.value,
                spread.timestamp,
            )
