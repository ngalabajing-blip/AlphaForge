"""Shared exception hierarchy used across all AlphaForge services."""

from __future__ import annotations


class AlphaForgeError(Exception):
    """Base for every AlphaForge-specific exception."""


# ── Configuration / startup ────────────────────────────────────────────────────
class ConfigError(AlphaForgeError):
    """Raised when required configuration is missing or invalid."""


class StartupError(AlphaForgeError):
    """Raised when a service cannot complete its startup sequence."""


# ── Datastores ─────────────────────────────────────────────────────────────────
class DatabaseError(AlphaForgeError):
    """Generic database error."""


class CacheError(AlphaForgeError):
    """Generic cache error."""


class KafkaError(AlphaForgeError):
    """Generic Kafka error."""


# ── Domain ─────────────────────────────────────────────────────────────────────
class UnsupportedChainError(AlphaForgeError):
    """Raised when an operation is attempted against an unknown / unsupported chain."""


class StrategyError(AlphaForgeError):
    """Base for DSL parsing and strategy execution errors."""


class StrategyParseError(StrategyError):
    """Raised when a strategy DSL document cannot be parsed."""


class StrategyValidationError(StrategyError):
    """Raised when a strategy passes parsing but fails semantic validation."""


class StrategyRuntimeError(StrategyError):
    """Raised when a strategy crashes during execution."""


class IndicatorError(StrategyError):
    """Raised when an indicator cannot be computed."""


class BacktestError(AlphaForgeError):
    """Raised when a backtest fails to complete."""


class AuditError(AlphaForgeError):
    """Raised by the smart-contract auditor."""


class NotificationError(AlphaForgeError):
    """Raised when a notification channel fails to deliver."""


# ── HTTP / API ─────────────────────────────────────────────────────────────────
class APIError(AlphaForgeError):
    status_code: int = 500

    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        if status_code is not None:
            self.status_code = status_code


class NotFound(APIError):
    status_code = 404


class Unauthorized(APIError):
    status_code = 401


class Forbidden(APIError):
    status_code = 403


class Conflict(APIError):
    status_code = 409


class RateLimited(APIError):
    status_code = 429
