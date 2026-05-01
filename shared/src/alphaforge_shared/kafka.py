"""
Thin async Kafka producer / consumer wrappers.

These wrappers are intentionally minimal — they exist to centralise:

* JSON (orjson) (de)serialisation of :class:`BaseEvent` payloads
* Topic-name and schema-version validation
* Standard Kafka client config (delivery semantics, retries)

Services should import :class:`EventProducer` / :class:`EventConsumer` rather
than instantiating ``aiokafka`` directly.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Awaitable, Callable
from typing import Any, Generic, TypeVar

import orjson

from alphaforge_shared.events import BaseEvent
from alphaforge_shared.exceptions import KafkaError
from alphaforge_shared.logging import get_logger
from alphaforge_shared.topics import Topic

E = TypeVar("E", bound=BaseEvent)
log = get_logger(__name__)


def _orjson_default(obj: Any) -> Any:
    if hasattr(obj, "model_dump"):
        return obj.model_dump(mode="json")
    raise TypeError(f"Cannot serialize {type(obj)}")


def serialize_event(event: BaseEvent) -> bytes:
    payload = event.model_dump(mode="json")
    return orjson.dumps(payload, default=_orjson_default)


def deserialize_event(raw: bytes, model: type[E]) -> E:
    obj = orjson.loads(raw)
    return model.model_validate(obj)


class EventProducer:
    """Async producer that takes :class:`BaseEvent` instances."""

    def __init__(self, bootstrap: str, *, client_id: str = "alphaforge") -> None:
        self.bootstrap = bootstrap
        self.client_id = client_id
        self._producer: Any = None
        self._lock = asyncio.Lock()

    async def start(self) -> None:
        async with self._lock:
            if self._producer is not None:
                return
            try:
                from aiokafka import AIOKafkaProducer  # type: ignore[import-not-found]
            except ImportError as exc:  # pragma: no cover
                raise KafkaError("aiokafka is not installed") from exc
            self._producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap,
                client_id=self.client_id,
                acks="all",
                enable_idempotence=True,
                compression_type="lz4",
            )
            await self._producer.start()
            log.info("kafka_producer_started", bootstrap=self.bootstrap)

    async def stop(self) -> None:
        async with self._lock:
            if self._producer is None:
                return
            await self._producer.stop()
            self._producer = None
            log.info("kafka_producer_stopped")

    async def publish(self, topic: Topic, event: BaseEvent, *, key: str | None = None) -> None:
        if self._producer is None:
            await self.start()
        if not isinstance(event, BaseEvent):
            raise KafkaError(f"event must be BaseEvent, got {type(event)}")
        if event.schema != topic.name:
            raise KafkaError(f"schema mismatch: event.schema={event.schema!r} topic={topic.name!r}")
        payload = serialize_event(event)
        await self._producer.send_and_wait(
            topic.name,
            payload,
            key=key.encode("utf-8") if key else None,
        )


class EventConsumer(Generic[E]):
    """Async consumer that yields parsed :class:`BaseEvent` subclasses."""

    def __init__(
        self,
        bootstrap: str,
        *,
        group_id: str,
        topics: list[Topic],
        model: type[E],
        auto_offset_reset: str = "latest",
    ) -> None:
        self.bootstrap = bootstrap
        self.group_id = group_id
        self.topics = topics
        self.model = model
        self.auto_offset_reset = auto_offset_reset
        self._consumer: Any = None

    async def start(self) -> None:
        try:
            from aiokafka import AIOKafkaConsumer  # type: ignore[import-not-found]
        except ImportError as exc:  # pragma: no cover
            raise KafkaError("aiokafka is not installed") from exc
        self._consumer = AIOKafkaConsumer(
            *(t.name for t in self.topics),
            bootstrap_servers=self.bootstrap,
            group_id=self.group_id,
            auto_offset_reset=self.auto_offset_reset,
            enable_auto_commit=False,
        )
        await self._consumer.start()
        log.info(
            "kafka_consumer_started",
            group=self.group_id,
            topics=[t.name for t in self.topics],
        )

    async def stop(self) -> None:
        if self._consumer is not None:
            await self._consumer.stop()
            self._consumer = None

    async def stream(self) -> AsyncIterator[E]:
        if self._consumer is None:
            await self.start()
        try:
            async for msg in self._consumer:
                try:
                    event = deserialize_event(msg.value, self.model)
                except Exception:  # pragma: no cover - defensive
                    log.exception("kafka_decode_failed", topic=msg.topic)
                    continue
                yield event
                await self._consumer.commit()
        finally:
            await self.stop()

    async def run(self, handler: Callable[[E], Awaitable[None]]) -> None:
        async for event in self.stream():
            try:
                await handler(event)
            except Exception:
                log.exception("kafka_handler_failed", event_id=event.event_id)
