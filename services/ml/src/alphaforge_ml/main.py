"""
ML service entrypoint.

Three coroutines run concurrently:

* ``anomaly_loop``  — consumes :data:`T_DEX_TRADES` & :data:`T_LIQUIDITY_DELTAS`,
  publishes :data:`T_ANOMALY` whenever a window scores above the threshold.
* ``sentiment_loop`` — consumes Twitter / Discord webhooks (synthetic for dev)
  and publishes :data:`T_SENTIMENT` per asset.
* ``prediction_loop`` — consumes :data:`T_PRICES` candles and publishes
  :data:`T_PRICE_PREDICTION`.
"""

from __future__ import annotations

import asyncio
import signal

from alphaforge_shared.logging import configure_logging, get_logger
from alphaforge_shared.telemetry import configure_tracing

from alphaforge_ml.config import get_settings
from alphaforge_ml.consumers.anomaly_loop import run_anomaly_loop
from alphaforge_ml.consumers.prediction_loop import run_prediction_loop
from alphaforge_ml.consumers.sentiment_loop import run_sentiment_loop

log = get_logger("alphaforge_ml.main")


async def run() -> None:
    settings = get_settings()
    configure_logging(level=settings.app_log_level, json_logs=settings.is_production)
    configure_tracing("alphaforge-ml", settings.otel_endpoint)
    log.info("ml_starting")

    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, stop.set)
        except NotImplementedError:
            pass

    tasks = [
        asyncio.create_task(run_anomaly_loop(stop)),
        asyncio.create_task(run_sentiment_loop(stop)),
        asyncio.create_task(run_prediction_loop(stop)),
    ]
    await stop.wait()
    log.info("ml_stopping")
    for t in tasks:
        t.cancel()
    for t in tasks:
        try:
            await t
        except asyncio.CancelledError:
            pass


def cli() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    cli()
