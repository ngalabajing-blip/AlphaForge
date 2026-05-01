from __future__ import annotations

from alphaforge_shared.events import AuditRequest
from alphaforge_shared.topics import T_AUDIT_REQUESTED
from sqlalchemy.ext.asyncio import AsyncSession

from alphaforge_api.repositories.audit import AuditRepository


class AuditService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = AuditRepository(session)

    async def enqueue(self, *, requested_by: str, chain: str, address: str, deep: bool):
        job = await self.repo.create(
            requested_by=requested_by,
            chain=chain,
            address=address,
            status="queued",
        )
        # publish to kafka topic — auditor service consumes it
        try:
            from alphaforge_api.core.kafka_client import kafka_producer

            await kafka_producer.producer.publish(
                T_AUDIT_REQUESTED,
                AuditRequest(
                    producer="alphaforge-api",
                    audit_id=job.id,
                    chain=chain,
                    address=address,
                    deep=deep,
                    requested_by=requested_by,
                ),
                key=address,
            )
        except Exception:
            # best effort — auditor will pick it up via DB polling
            pass
        return job
