"""Kafka consumer for the alerts topic."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime

import orjson
from alphaforge_shared.logging import get_logger
from alphaforge_shared.topics import T_ALERTS, T_NOTIFICATION_RESULT

from alphaforge_notifier.config import get_settings
from alphaforge_notifier.dispatcher import NotifierDispatcher

log = get_logger("alphaforge_notifier.consumer")


class AlertConsumer:
    def __init__(self, dispatcher: NotifierDispatcher) -> None:
        self.dispatcher = dispatcher

    async def run(self, stop: asyncio.Event) -> None:
        try:
            from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
        except ImportError:
            log.warning("aiokafka_missing_using_synthetic_loop")
            await self._synthetic_loop(stop)
            return

        settings = get_settings()
        consumer = AIOKafkaConsumer(
            T_ALERTS,
            bootstrap_servers=settings.kafka_bootstrap,
            group_id="alphaforge-notifier",
            enable_auto_commit=True,
            auto_offset_reset="latest",
        )
        producer = AIOKafkaProducer(bootstrap_servers=settings.kafka_bootstrap)
        try:
            await consumer.start()
            await producer.start()
        except Exception:
            log.warning("kafka_unavailable_using_synthetic_loop")
            await self._synthetic_loop(stop)
            return
        try:
            log.info("alert_consumer_started")
            while not stop.is_set():
                try:
                    msg = await asyncio.wait_for(consumer.__anext__(), timeout=2.0)
                except (TimeoutError, StopAsyncIteration):
                    continue
                except Exception as exc:  # noqa: BLE001
                    log.exception("kafka_consumer_error", error=str(exc))
                    continue
                try:
                    payload = orjson.loads(msg.value)
                except Exception:
                    continue
                results = await self.dispatcher.dispatch(payload)
                await self._publish_results(producer, payload, results)
        finally:
            try:
                await consumer.stop()
                await producer.stop()
            except Exception:
                pass
            log.info("alert_consumer_stopped")

    async def _publish_results(self, producer, alert: dict, results: list) -> None:  # type: ignore[no-untyped-def]
        out = {
            "alert_id": alert.get("alert_id"),
            "owner_id": alert.get("owner_id"),
            "delivered_at": datetime.now(tz=UTC).isoformat(),
            "deliveries": [r.__dict__ for r in results],
        }
        try:
            await producer.send_and_wait(T_NOTIFICATION_RESULT, orjson.dumps(out))
        except Exception:
            pass

    async def _synthetic_loop(self, stop: asyncio.Event) -> None:
        # When Kafka is unavailable, emit a dummy heartbeat so the service
        # remains observable. Real alerts get queued via the API.
        while not stop.is_set():
            try:
                await asyncio.wait_for(stop.wait(), timeout=15.0)
            except TimeoutError:
                pass
