"""Kafka sink — wraps :class:`EventProducer` with metric counters."""

from __future__ import annotations

from alphaforge_shared.events import BaseEvent
from alphaforge_shared.kafka import EventProducer
from alphaforge_shared.logging import get_logger
from alphaforge_shared.topics import Topic
from prometheus_client import Counter

log = get_logger("alphaforge_ingestor.sink")

EVENTS_PUBLISHED = Counter(
    "alphaforge_ingestor_events_total",
    "Events published by the ingestor",
    ["topic", "chain"],
)
EVENTS_FAILED = Counter(
    "alphaforge_ingestor_failures_total",
    "Failed publishes",
    ["topic", "chain", "reason"],
)


class KafkaSink:
    def __init__(self, *, bootstrap: str, client_id: str = "alphaforge-ingestor") -> None:
        self.producer = EventProducer(bootstrap, client_id=client_id)
        self._started = False

    async def start(self) -> None:
        try:
            await self.producer.start()
            self._started = True
        except Exception:
            log.exception("kafka_sink_start_failed")
            self._started = False

    async def stop(self) -> None:
        if self._started:
            await self.producer.stop()
            self._started = False

    @property
    def is_started(self) -> bool:
        return self._started

    async def publish(
        self,
        topic: Topic,
        event: BaseEvent,
        *,
        key: str | None = None,
        chain: str | None = None,
    ) -> None:
        chain_label = chain or "unknown"
        if not self._started:
            EVENTS_FAILED.labels(topic.name, chain_label, "not_started").inc()
            log.debug("sink_not_started", topic=topic.name)
            return
        try:
            await self.producer.publish(topic, event, key=key)
            EVENTS_PUBLISHED.labels(topic.name, chain_label).inc()
        except Exception as exc:  # noqa: BLE001
            EVENTS_FAILED.labels(topic.name, chain_label, type(exc).__name__).inc()
            log.exception("sink_publish_failed", topic=topic.name, error=str(exc))
