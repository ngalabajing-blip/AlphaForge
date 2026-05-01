from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from alphaforge_api.models.audit import AuditJob


class AuditRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, **kwargs: Any) -> AuditJob:
        job = AuditJob(**kwargs)
        self.session.add(job)
        await self.session.flush()
        return job

    async def get(self, audit_id: str) -> Optional[AuditJob]:
        return await self.session.get(AuditJob, audit_id)

    async def list(self, *, limit: int = 50, offset: int = 0,
                   address: Optional[str] = None) -> list[AuditJob]:
        stmt = select(AuditJob)
        if address:
            stmt = stmt.where(AuditJob.address == address.lower())
        stmt = stmt.order_by(AuditJob.created_at.desc()).limit(limit).offset(offset)
        return list((await self.session.execute(stmt)).scalars().all())

    async def update_status(self, job: AuditJob, status: str, *, error: Optional[str] = None) -> AuditJob:
        job.status = status
        if status == "running" and job.started_at is None:
            job.started_at = datetime.now(tz=timezone.utc)
        if status in ("completed", "failed"):
            job.completed_at = datetime.now(tz=timezone.utc)
        if error:
            job.error = error
        await self.session.flush()
        return job

    async def finalize(self, job: AuditJob, *, risk_score: float, risk_level: str,
                       summary: str, findings: list[dict], bytecode_size: int,
                       has_source: bool) -> AuditJob:
        job.risk_score = risk_score  # type: ignore[assignment]
        job.risk_level = risk_level
        job.summary = summary
        job.findings = findings
        job.bytecode_size = bytecode_size
        job.has_source = has_source
        job.status = "completed"
        job.completed_at = datetime.now(tz=timezone.utc)
        await self.session.flush()
        return job
