"""
Unified structured logging.

Every service should call :func:`configure_logging` once at startup. Log lines
are emitted as JSON in production and as a friendly key/value layout in dev.
"""

from __future__ import annotations

import logging
import os
import sys
from collections.abc import Mapping
from typing import Any

import structlog
from structlog.types import EventDict, Processor


def _add_service(_, __, event_dict: EventDict) -> EventDict:
    event_dict.setdefault("service", os.getenv("SERVICE_NAME", "alphaforge"))
    return event_dict


def _drop_color_message(_, __, event_dict: EventDict) -> EventDict:
    event_dict.pop("color_message", None)
    return event_dict


def configure_logging(level: str | int = "INFO", *, json_logs: bool | None = None) -> None:
    """
    Configure structlog + stdlib logging.

    Parameters
    ----------
    level
        Minimum log level (string name or numeric).
    json_logs
        If True, emit JSON; if False, emit pretty key/value. If None (default),
        decide by whether ``APP_ENV=production``.
    """
    if json_logs is None:
        json_logs = os.getenv("APP_ENV", "development").lower() == "production"

    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)

    timestamper = structlog.processors.TimeStamper(fmt="iso", utc=True)

    processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        timestamper,
        _add_service,
        _drop_color_message,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    if json_logs:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer(colors=True))

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(level),
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )

    # Make the root stdlib logger respect the same level so noisy libs are filtered.
    logging.basicConfig(level=level, stream=sys.stdout, format="%(message)s")


def get_logger(name: str | None = None, **initial: Any) -> structlog.stdlib.BoundLogger:
    """Return a structlog logger bound with ``initial`` context."""
    log = structlog.get_logger(name) if name else structlog.get_logger()
    if initial:
        log = log.bind(**initial)
    return log


def bind_request_context(request_id: str, **extra: Any) -> Mapping[str, Any]:
    """Bind contextvars for a request scope. Returns the bound mapping."""
    structlog.contextvars.bind_contextvars(request_id=request_id, **extra)
    return {"request_id": request_id, **extra}
