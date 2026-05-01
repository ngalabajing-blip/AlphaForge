"""Auditor service entrypoint — listens for audit-requested events."""

from __future__ import annotations

import asyncio
import signal

from alphaforge_shared.logging import configure_logging, get_logger
from alphaforge_shared.telemetry import configure_tracing

from alphaforge_auditor.config import get_settings
from alphaforge_auditor.consumer import AuditConsumer

log = get_logger("alphaforge_auditor.main")


async def run() -> None:
    settings = get_settings()
    configure_logging(level=settings.app_log_level, json_logs=settings.is_production)
    configure_tracing("alphaforge-auditor", settings.otel_endpoint)
    log.info("auditor_starting")

    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, stop.set)
        except NotImplementedError:
            pass

    consumer = AuditConsumer()
    task = asyncio.create_task(consumer.run(stop))
    await stop.wait()
    log.info("auditor_stopping")
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


def cli() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    cli()
