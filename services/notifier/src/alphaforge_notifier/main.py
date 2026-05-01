"""Notifier service entrypoint — consumes alerts from Kafka and fans out."""
from __future__ import annotations

import asyncio
import signal

from alphaforge_notifier.config import get_settings
from alphaforge_notifier.dispatcher import NotifierDispatcher
from alphaforge_notifier.consumer import AlertConsumer
from alphaforge_shared.logging import configure_logging, get_logger
from alphaforge_shared.telemetry import configure_tracing

log = get_logger("alphaforge_notifier.main")


async def run() -> None:
    settings = get_settings()
    configure_logging(level=settings.app_log_level, json_logs=settings.is_production)
    configure_tracing("alphaforge-notifier", settings.otel_endpoint)
    log.info("notifier_starting")

    dispatcher = NotifierDispatcher()
    await dispatcher.start()
    consumer = AlertConsumer(dispatcher)

    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, stop.set)
        except NotImplementedError:
            pass

    consumer_task = asyncio.create_task(consumer.run(stop))
    await stop.wait()
    log.info("notifier_stopping")
    consumer_task.cancel()
    try:
        await consumer_task
    except asyncio.CancelledError:
        pass
    await dispatcher.stop()


def cli() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    cli()
