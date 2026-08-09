"""Database connection and initialization."""
import asyncpg


class Database:
    """PostgreSQL database connection pool."""

    def __init__(self, db_url: str):
        """Initialize with database URL."""
        self.db_url = db_url
        self.pool = None

    async def connect(self):
        """Create connection pool."""
        self.pool = await asyncpg.create_pool(
            self.db_url,
            min_size=5,
            max_size=20,
            command_timeout=60,
        )

    async def disconnect(self):
        """Close connection pool."""
        if self.pool:
            await self.pool.close()

    async def initialize_schema(self):
        """Create tables if they don't exist."""
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS price_bars (
                    instrument TEXT NOT NULL,
                    timestamp TIMESTAMPTZ NOT NULL,
                    open FLOAT NOT NULL,
                    high FLOAT NOT NULL,
                    low FLOAT NOT NULL,
                    close FLOAT NOT NULL,
                    volume INTEGER NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    PRIMARY KEY (instrument, timestamp)
                );

                CREATE TABLE IF NOT EXISTS spreads (
                    long_instrument TEXT NOT NULL,
                    short_instrument TEXT NOT NULL,
                    value FLOAT NOT NULL,
                    timestamp TIMESTAMPTZ NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    PRIMARY KEY (long_instrument, short_instrument, timestamp)
                );

                CREATE TABLE IF NOT EXISTS signals (
                    signal_id TEXT PRIMARY KEY,
                    strategy_id TEXT NOT NULL,
                    instrument_long TEXT NOT NULL,
                    instrument_short TEXT NOT NULL,
                    action TEXT NOT NULL CHECK (action IN ('BUY', 'SELL', 'NEUTRAL')),
                    confidence FLOAT NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
                    timestamp TIMESTAMPTZ NOT NULL,
                    rationale TEXT NOT NULL,
                    expected_hold_days INTEGER NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );

                CREATE INDEX IF NOT EXISTS idx_signals_timestamp ON signals(timestamp DESC);
                CREATE INDEX IF NOT EXISTS idx_signals_strategy ON signals(strategy_id);
                CREATE INDEX IF NOT EXISTS idx_price_bars_timestamp ON price_bars(timestamp DESC);
                CREATE INDEX IF NOT EXISTS idx_spreads_timestamp ON spreads(timestamp DESC);
                """
            )
