"""PostgreSQL signal repository adapter."""
from typing import List
from uuid import uuid4

from src.domain.entities.signal import Signal
from src.ports.repository import ISignalRepository


class PostgresSignalRepository(ISignalRepository):
    """Concrete PostgreSQL signal repository."""

    def __init__(self, db_pool):
        """Initialize with database connection pool."""
        self.db_pool = db_pool

    async def save_signal(self, signal: Signal) -> str:
        """Save a signal, return signal_id."""
        signal_id = str(uuid4())
        async with self.db_pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO signals
                (signal_id, strategy_id, instrument_long, instrument_short, action, confidence, timestamp, rationale, expected_hold_days)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                """,
                signal_id,
                signal.strategy_id,
                signal.instrument_long,
                signal.instrument_short,
                signal.action,
                signal.confidence,
                signal.timestamp,
                signal.rationale,
                signal.expected_hold_days,
            )
        return signal_id

    async def get_latest_signals(self, limit: int = 10) -> List[Signal]:
        """Fetch the most recent signals."""
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT signal_id, strategy_id, instrument_long, instrument_short, action, confidence, timestamp, rationale, expected_hold_days
                FROM signals
                ORDER BY timestamp DESC
                LIMIT $1
                """,
                limit,
            )
            return [
                Signal(
                    strategy_id=row["strategy_id"],
                    instrument_long=row["instrument_long"],
                    instrument_short=row["instrument_short"],
                    action=row["action"],
                    confidence=row["confidence"],
                    timestamp=row["timestamp"],
                    rationale=row["rationale"],
                    expected_hold_days=row["expected_hold_days"],
                )
                for row in rows
            ]

    async def get_signals_by_strategy(self, strategy_id: str, limit: int = 10) -> List[Signal]:
        """Fetch signals for a strategy."""
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT signal_id, strategy_id, instrument_long, instrument_short, action, confidence, timestamp, rationale, expected_hold_days
                FROM signals
                WHERE strategy_id = $1
                ORDER BY timestamp DESC
                LIMIT $2
                """,
                strategy_id,
                limit,
            )
            return [
                Signal(
                    strategy_id=row["strategy_id"],
                    instrument_long=row["instrument_long"],
                    instrument_short=row["instrument_short"],
                    action=row["action"],
                    confidence=row["confidence"],
                    timestamp=row["timestamp"],
                    rationale=row["rationale"],
                    expected_hold_days=row["expected_hold_days"],
                )
                for row in rows
            ]
