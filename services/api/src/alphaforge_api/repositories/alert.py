from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from alphaforge_api.models.alert import Alert, AlertDelivery


class AlertRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, alert_id: str) -> Optional[Alert]:
        return await self.session.get(Alert, alert_id)

    async def list(self, *, owner_id: str) -> list[Alert]:
        stmt = select(Alert).where(Alert.owner_id == owner_id).order_by(Alert.created_at.desc())
        return list((await self.session.execute(stmt)).scalars().all())

    async def create(self, **kwargs: Any) -> Alert:
        a = Alert(**kwargs)
        self.session.add(a)
        await self.session.flush()
        return a

    async def update(self, alert: Alert, **kwargs: Any) -> Alert:
        for key, value in kwargs.items():
            if value is not None:
                setattr(alert, key, value)
        await self.session.flush()
        return alert

    async def delete(self, alert: Alert) -> None:
        await self.session.delete(alert)
        await self.session.flush()

    async def mark_fired(self, alert: Alert) -> None:
        alert.fire_count += 1
        alert.last_fired_at = datetime.now(tz=timezone.utc)
        await self.session.flush()

    async def record_delivery(
        self,
        *,
        alert_id: str,
        channel: str,
        success: bool,
        error: Optional[str],
        payload: dict,
    ) -> AlertDelivery:
        d = AlertDelivery(
            alert_id=alert_id,
            channel=channel,
            delivered_at=datetime.now(tz=timezone.utc),
            success=success,
            error=error,
            payload=payload,
        )
        self.session.add(d)
        await self.session.flush()
        return d
