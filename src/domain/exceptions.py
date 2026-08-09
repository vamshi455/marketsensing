"""Domain exceptions."""


class DomainError(Exception):
    """Base domain exception."""


class InsufficientDataError(DomainError):
    """Raised when not enough data to calculate signal."""


class InvalidSignalError(DomainError):
    """Raised when signal parameters are invalid."""


class InvalidSpreadError(DomainError):
    """Raised when spread data is malformed."""


class RiskLimitExceededError(DomainError):
    """Raised when a trade would exceed risk limits."""
