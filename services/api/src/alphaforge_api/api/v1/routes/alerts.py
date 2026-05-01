from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from alphaforge_api.core.database import get_session
from alphaforge_api.core.security import CurrentUser, get_current_user, require_permission
from alphaforge_api.repositories.alert import AlertRepository
from alphaforge_api.schemas.alert import AlertCreate, AlertOut, AlertUpdate

router = APIRouter(prefix="/alerts")


@router.get("", response_model=list[AlertOut])
async def list_alerts(
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[AlertOut]:
    repo = AlertRepository(session)
    items = await repo.list(owner_id=user.user_id)
    return [AlertOut.model_validate(a) for a in items]


@router.post("", response_model=AlertOut, status_code=201)
async def create_alert(
    payload: AlertCreate,
    user: CurrentUser = Depends(require_permission("alerts:manage")),
    session: AsyncSession = Depends(get_session),
) -> AlertOut:
    repo = AlertRepository(session)
    alert = await repo.create(
        owner_id=user.user_id,
        name=payload.name,
        description=payload.description,
        rule_type=payload.rule_type,
        rule_config=payload.rule_config,
        channels=payload.channels,
        cooldown_seconds=payload.cooldown_seconds,
        enabled=payload.enabled,
    )
    return AlertOut.model_validate(alert)


@router.patch("/{alert_id}", response_model=AlertOut)
async def update_alert(
    alert_id: str,
    payload: AlertUpdate,
    user: CurrentUser = Depends(require_permission("alerts:manage")),
    session: AsyncSession = Depends(get_session),
) -> AlertOut:
    repo = AlertRepository(session)
    alert = await repo.get(alert_id)
    if alert is None or alert.owner_id != user.user_id:
        raise HTTPException(status_code=404, detail="alert not found")
    updated = await repo.update(alert, **payload.model_dump(exclude_unset=True))
    return AlertOut.model_validate(updated)


@router.delete("/{alert_id}", status_code=204)
async def delete_alert(
    alert_id: str,
    user: CurrentUser = Depends(require_permission("alerts:manage")),
    session: AsyncSession = Depends(get_session),
) -> None:
    repo = AlertRepository(session)
    alert = await repo.get(alert_id)
    if alert is None or alert.owner_id != user.user_id:
        raise HTTPException(status_code=404, detail="alert not found")
    await repo.delete(alert)
