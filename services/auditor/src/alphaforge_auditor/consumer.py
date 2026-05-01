"""Kafka consumer that drives the audit pipeline."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime

import orjson
from alphaforge_shared.logging import get_logger
from alphaforge_shared.topics import T_AUDIT_REPORT, T_AUDIT_REQUESTED

from alphaforge_auditor.config import get_settings
from alphaforge_auditor.engine import AuditEngine

log = get_logger("alphaforge_auditor.consumer")


class AuditConsumer:
    def __init__(self) -> None:
        self.engine = AuditEngine()

    async def run(self, stop: asyncio.Event) -> None:
        try:
            from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
        except ImportError:
            log.warning("aiokafka_missing_idle")
            await stop.wait()
            return

        settings = get_settings()
        consumer = AIOKafkaConsumer(
            T_AUDIT_REQUESTED,
            bootstrap_servers=settings.kafka_bootstrap,
            group_id="alphaforge-auditor",
            enable_auto_commit=True,
            auto_offset_reset="latest",
        )
        producer = AIOKafkaProducer(bootstrap_servers=settings.kafka_bootstrap)
        try:
            await consumer.start()
            await producer.start()
        except Exception:
            log.warning("kafka_unavailable_idle")
            await stop.wait()
            return
        try:
            while not stop.is_set():
                try:
                    msg = await asyncio.wait_for(consumer.__anext__(), timeout=2.0)
                except (TimeoutError, StopAsyncIteration):
                    continue
                except Exception as exc:  # noqa: BLE001
                    log.exception("kafka_error", error=str(exc))
                    continue
                try:
                    payload = orjson.loads(msg.value)
                except Exception:
                    continue
                report = await self.engine.run_audit(payload)
                report["received_at"] = datetime.now(tz=UTC).isoformat()
                try:
                    await producer.send_and_wait(T_AUDIT_REPORT, orjson.dumps(report))
                except Exception:
                    pass
        finally:
            try:
                await consumer.stop()
                await producer.stop()
            except Exception:
                pass
