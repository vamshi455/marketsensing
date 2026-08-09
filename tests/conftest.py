"""Pytest configuration and shared fixtures."""
import pytest

from src.adapters.config.yaml_loader import YamlConfigLoader
from src.adapters.logger.console_logger import ConsoleLogger
from src.adapters.notifiers.console_notifier import ConsoleNotifier
from src.adapters.repositories.postgres_price import PostgresPriceRepository
from src.adapters.repositories.postgres_signal import PostgresSignalRepository
from src.adapters.repositories.postgres_spread import PostgresSpreadRepository
from src.application.use_cases.generate_signal import GenerateSignalUseCase
from tests.fixtures.fake_repositories import (
    FakePriceRepository,
    FakeSignalRepository,
    FakeSpreadRepository,
)


@pytest.fixture
def console_logger():
    """Console logger fixture."""
    return ConsoleLogger()


@pytest.fixture
def console_notifier():
    """Console notifier fixture."""
    return ConsoleNotifier()


@pytest.fixture
def yaml_config_loader():
    """YAML config loader fixture."""
    return YamlConfigLoader("config")


@pytest.fixture
def fake_price_repo():
    """Fake (in-memory) price repository."""
    return FakePriceRepository()


@pytest.fixture
def fake_spread_repo():
    """Fake (in-memory) spread repository."""
    return FakeSpreadRepository()


@pytest.fixture
def fake_signal_repo():
    """Fake (in-memory) signal repository."""
    return FakeSignalRepository()


@pytest.fixture
def generate_signal_use_case(
    fake_price_repo,
    fake_spread_repo,
    fake_signal_repo,
    yaml_config_loader,
    console_logger,
    console_notifier,
):
    """Generate signal use case with all fake adapters."""
    return GenerateSignalUseCase(
        price_repo=fake_price_repo,
        spread_repo=fake_spread_repo,
        signal_repo=fake_signal_repo,
        config=yaml_config_loader,
        logger=console_logger,
        notifier=console_notifier,
    )
