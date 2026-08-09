"""Generate signal use case."""
from src.application.dto.signal_dto import GenerateSignalRequest, GenerateSignalResponse
from src.domain.exceptions import InsufficientDataError
from src.domain.services.risk_checker import RiskChecker, RiskLimits
from src.domain.services.spread_signal_service import SpreadSignalService
from src.domain.value_objects.spread_statistics import SpreadStatistics
from src.ports.config import IConfigLoader
from src.ports.logger import ILogger
from src.ports.notifier import INotifier
from src.ports.repository import IPriceRepository, ISignalRepository, ISpreadRepository


class GenerateSignalUseCase:
    """Orchestrate signal generation."""

    def __init__(
        self,
        price_repo: IPriceRepository,
        spread_repo: ISpreadRepository,
        signal_repo: ISignalRepository,
        config: IConfigLoader,
        logger: ILogger,
        notifier: INotifier,
    ):
        """Initialize with dependencies (injected at wiring time)."""
        self.price_repo = price_repo
        self.spread_repo = spread_repo
        self.signal_repo = signal_repo
        self.config = config
        self.logger = logger
        self.notifier = notifier
        self.signal_service = SpreadSignalService()

    async def execute(self, request: GenerateSignalRequest) -> GenerateSignalResponse:
        """Generate a signal from request."""
        self.logger.info(
            "Generating signal",
            strategy=request.strategy_id,
            pair=f"{request.long_instrument}/{request.short_instrument}",
        )

        # Get latest prices
        long_price = await self.price_repo.get_latest_price(request.long_instrument)
        short_price = await self.price_repo.get_latest_price(request.short_instrument)

        if long_price is None or short_price is None:
            msg = "Missing price data for signal generation"
            self.logger.error(msg)
            raise InsufficientDataError(msg)

        # Calculate current spread
        current_spread = long_price.close - short_price.close

        # Load strategy config (spread calculation window, z-score threshold, etc.)
        strategy_config = self.config.load_strategy(request.strategy_id)
        lookback_days = strategy_config.get("lookback_days", 60)

        # Get historical spread data to compute statistics
        # (In production, this would be materialized in a features table)
        # For MVP, we stub this with reasonable defaults
        try:
            spread_stats = SpreadStatistics(
                mean=strategy_config.get("mean_spread", 0.0),
                std=strategy_config.get("std_spread", 1.0),
                median=strategy_config.get("median_spread", 0.0),
                p25=strategy_config.get("p25_spread", -1.0),
                p75=strategy_config.get("p75_spread", 1.0),
            )
        except Exception as e:
            self.logger.error(f"Failed to calculate spread statistics: {e}")
            raise InsufficientDataError(f"Cannot compute spread stats: {e}")

        # Generate signal from domain service (pure logic)
        signal = self.signal_service.generate_signal(
            strategy_id=request.strategy_id,
            long_instrument=request.long_instrument,
            short_instrument=request.short_instrument,
            current_spread=current_spread,
            spread_stats=spread_stats,
            z_score_threshold=request.z_score_threshold,
            expected_hold_days=request.expected_hold_days,
        )

        # Apply risk filters
        risk_limits = RiskLimits(
            max_position_size=strategy_config.get("max_position_size", 100),
            max_daily_loss=strategy_config.get("max_daily_loss", 10000.0),
            max_correlation_to_existing=strategy_config.get("max_correlation", 0.8),
            min_confidence_threshold=strategy_config.get("min_confidence", 0.3),
        )
        risk_checker = RiskChecker(risk_limits)
        passes_risk, risk_reason = risk_checker.check_signal(signal)

        if not passes_risk:
            self.logger.warning(f"Signal rejected by risk filter: {risk_reason}")
            signal.action = "NEUTRAL"
            signal.confidence = 0.0

        # Persist signal
        signal_id = await self.signal_repo.save_signal(signal)
        self.logger.info(f"Signal saved", signal_id=signal_id, action=signal.action)

        # Notify (broadcast to subscribers)
        await self.notifier.notify_signal(signal)

        # Return response
        return GenerateSignalResponse(
            strategy_id=signal.strategy_id,
            instrument_long=signal.instrument_long,
            instrument_short=signal.instrument_short,
            action=signal.action,
            confidence=signal.confidence,
            rationale=signal.rationale,
            timestamp=signal.timestamp,
        )
