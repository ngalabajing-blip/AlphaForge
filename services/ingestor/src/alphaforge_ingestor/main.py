"""
Ingestor entrypoint.

The service launches one task per enabled chain. Each task wraps a chain
adapter (EVM / Solana / Cosmos), reconnects on failure, and publishes
normalised events to Kafka.
"""

from __future__ import annotations

import asyncio
import signal

from alphaforge_shared.chains import get_chain
from alphaforge_shared.logging import configure_logging, get_logger
from alphaforge_shared.telemetry import configure_tracing

from alphaforge_ingestor.config import get_settings
from alphaforge_ingestor.kafka_sink import KafkaSink
from alphaforge_ingestor.pipeline.dispatcher import ChainDispatcher

log = get_logger("alphaforge_ingestor.main")


async def run() -> None:
    settings = get_settings()
    configure_logging(level=settings.app_log_level, json_logs=settings.is_production)
    configure_tracing("alphaforge-ingestor", settings.otel_endpoint)
    log.info("ingestor_starting", chains=settings.enabled_chains)

    sink = KafkaSink(bootstrap=settings.kafka_bootstrap, client_id="alphaforge-ingestor")
    await sink.start()

    dispatcher = ChainDispatcher(sink=sink)
    tasks: list[asyncio.Task[None]] = []
    for chain_id in settings.enabled_chains:
        try:
            spec = get_chain(chain_id)
        except KeyError:
            log.warning("ingestor_unknown_chain", chain=chain_id)
            continue
        task = asyncio.create_task(dispatcher.run_chain(spec), name=f"chain:{chain_id}")
        tasks.append(task)

    stop_event = asyncio.Event()

    def _stop(*_):  # type: ignore[no-untyped-def]
        log.info("ingestor_signal_stop")
        stop_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _stop)
        except NotImplementedError:
            pass  # Windows / non-main thread

    await stop_event.wait()
    log.info("ingestor_shutting_down", tasks=len(tasks))

    for t in tasks:
        t.cancel()
    for t in tasks:
        try:
            await t
        except asyncio.CancelledError:
            pass
    await sink.stop()
    log.info("ingestor_stopped")


def cli() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    cli()
