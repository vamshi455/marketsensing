"""Console notifier adapter (for development)."""
from src.domain.entities.signal import Signal
from src.ports.notifier import INotifier


class ConsoleNotifier(INotifier):
    """Simple console notifier for development."""

    async def notify_signal(self, signal: Signal) -> None:
        """Broadcast a signal to stdout."""
        print(f"\n{'='*60}")
        print(f"SIGNAL: {signal.strategy_id}")
        print(f"Action: {signal.action} (confidence: {signal.confidence:.2f})")
        print(f"Pair: {signal.instrument_long} / {signal.instrument_short}")
        print(f"Rationale: {signal.rationale}")
        print(f"Expected hold: {signal.expected_hold_days} days")
        print(f"{'='*60}\n")

    async def notify_error(self, error_message: str) -> None:
        """Broadcast an error message."""
        print(f"\n[ERROR] {error_message}\n")
