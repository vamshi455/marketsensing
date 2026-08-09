"""FastAPI application with hexagonal architecture."""
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.application.dto.signal_dto import GenerateSignalRequest, GenerateSignalResponse
from src.infrastructure.container import Container
from src.infrastructure.database import Database

# Initialize database and container
DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost/marketsensing")
db = Database(DB_URL)
container = None


app = FastAPI(
    title="MarketSensing Signal API",
    description="Trading signal generation platform",
    version="0.1.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    """Initialize database and container on startup."""
    global container
    await db.connect()
    await db.initialize_schema()
    container = Container(db)
    print("✓ Database connected and initialized")
    print("✓ Container wired")


@app.on_event("shutdown")
async def shutdown():
    """Close database on shutdown."""
    await db.disconnect()
    print("✓ Database disconnected")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "version": "0.1.0"}


@app.post("/signals/generate", response_model=GenerateSignalResponse)
async def generate_signal(request: GenerateSignalRequest):
    """
    Generate a trading signal.

    - **strategy_id**: Strategy identifier (e.g., "spread_midland_cushing")
    - **long_instrument**: Long leg (e.g., "WTI_MIDLAND")
    - **short_instrument**: Short leg (e.g., "WTI_CUSHING")
    - **z_score_threshold**: Entry threshold in standard deviations (default 2.0)
    """
    try:
        use_case = container.generate_signal_use_case()
        response = await use_case.execute(request)
        return response
    except Exception as e:
        container.logger.error(f"Signal generation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/signals/latest")
async def get_latest_signals(limit: int = 10):
    """Fetch the most recent signals."""
    try:
        signals = await container.signal_repo.get_latest_signals(limit)
        return {
            "signals": [
                {
                    "strategy": s.strategy_id,
                    "pair": f"{s.instrument_long}/{s.instrument_short}",
                    "action": s.action,
                    "confidence": s.confidence,
                    "timestamp": s.timestamp.isoformat(),
                    "rationale": s.rationale,
                }
                for s in signals
            ]
        }
    except Exception as e:
        container.logger.error(f"Failed to fetch signals: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch signals")


@app.get("/signals/strategy/{strategy_id}")
async def get_signals_by_strategy(strategy_id: str, limit: int = 10):
    """Fetch signals for a specific strategy."""
    try:
        signals = await container.signal_repo.get_signals_by_strategy(strategy_id, limit)
        return {
            "strategy": strategy_id,
            "count": len(signals),
            "signals": [
                {
                    "action": s.action,
                    "confidence": s.confidence,
                    "timestamp": s.timestamp.isoformat(),
                    "rationale": s.rationale,
                }
                for s in signals
            ],
        }
    except Exception as e:
        container.logger.error(f"Failed to fetch strategy signals: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch signals")


@app.get("/prices/{instrument}")
async def get_latest_price(instrument: str):
    """Fetch the latest price for an instrument."""
    try:
        price = await container.price_repo.get_latest_price(instrument)
        if price is None:
            raise HTTPException(status_code=404, detail=f"No price data for {instrument}")
        return {
            "instrument": price.instrument,
            "timestamp": price.timestamp.isoformat(),
            "open": price.open,
            "high": price.high,
            "low": price.low,
            "close": price.close,
            "volume": price.volume,
        }
    except HTTPException:
        raise
    except Exception as e:
        container.logger.error(f"Failed to fetch price: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch price")


@app.get("/spreads/{long}/{short}")
async def get_latest_spread(long: str, short: str):
    """Fetch the latest spread between two instruments."""
    try:
        spread = await container.spread_repo.get_latest_spread(long, short)
        if spread is None:
            raise HTTPException(
                status_code=404, detail=f"No spread data for {long}/{short}"
            )
        return {
            "long_instrument": spread.long_instrument,
            "short_instrument": spread.short_instrument,
            "value": spread.value,
            "timestamp": spread.timestamp.isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        container.logger.error(f"Failed to fetch spread: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch spread")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
