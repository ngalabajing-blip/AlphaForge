"""API-side Kafka producer singleton (wraps shared :class:`EventProducer`)."""
from __future__ import annotations

from alphaforge_api.core.config import get_settings
from alphaforge_shared.kafka import EventProducer
from alphaforge_shared.logging import get_logger

log = get_logger("alphaforge_api.kafka")


class APIKafkaProducer:
    def __init__(self) -> None:
        self._producer: EventProducer | None = None
        self._started = False

    @property
    def is_started(self) -> bool:
        return self._started

    async def start(self) -> None:
        if self._started:
            return
        try:
            settings = get_settings()
            self._producer = EventProducer(settings.kafka_bootstrap, client_id="alphaforge-api")
            await self._producer.start()
            self._started = True
        except Exception:
            log.exception("kafka_start_failed")
            self._started = False

    async def stop(self) -> None:
        if self._producer is not None:
            try:
                await self._producer.stop()
            except Exception:
                log.exception("kafka_stop_failed")
        self._started = False

    @property
    def producer(self) -> EventProducer:
        if self._producer is None:
            raise RuntimeError("kafka producer not started")
        return self._producer


kafka_producer = APIKafkaProducer()
