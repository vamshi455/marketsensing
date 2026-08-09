"""Dependency injection container."""
from src.adapters.config.yaml_loader import YamlConfigLoader
from src.adapters.logger.console_logger import ConsoleLogger
from src.adapters.notifiers.console_notifier import ConsoleNotifier
from src.adapters.repositories.postgres_price import PostgresPriceRepository
from src.adapters.repositories.postgres_signal import PostgresSignalRepository
from src.adapters.repositories.postgres_spread import PostgresSpreadRepository
from src.application.use_cases.generate_signal import GenerateSignalUseCase
from src.infrastructure.database import Database


class Container:
    """Dependency injection container (wiring all adapters and use cases)."""

    def __init__(self, db: Database, config_dir: str = "config"):
        """Initialize with database and config directory."""
        self.db = db

        # Instantiate adapters
        self.config = YamlConfigLoader(config_dir)
        self.logger = ConsoleLogger()
        self.notifier = ConsoleNotifier()
        self.price_repo = PostgresPriceRepository(db.pool)
        self.spread_repo = PostgresSpreadRepository(db.pool)
        self.signal_repo = PostgresSignalRepository(db.pool)

    def generate_signal_use_case(self) -> GenerateSignalUseCase:
        """Create and return the use case (wired with all dependencies)."""
        return GenerateSignalUseCase(
            price_repo=self.price_repo,
            spread_repo=self.spread_repo,
            signal_repo=self.signal_repo,
            config=self.config,
            logger=self.logger,
            notifier=self.notifier,
        )
