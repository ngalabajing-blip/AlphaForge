from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from alphaforge_api.core.database import get_session
from alphaforge_api.core.security import CurrentUser, get_current_user, require_permission
from alphaforge_api.repositories.audit import AuditRepository
from alphaforge_api.schemas.audit import AuditOut, AuditRequestIn
from alphaforge_api.services.audit_service import AuditService
from alphaforge_shared.chains import supports_chain
from alphaforge_shared.utils import normalise_address

router = APIRouter(prefix="/audits")


@router.post("", response_model=AuditOut, status_code=202)
async def request_audit(
    payload: AuditRequestIn,
    user: CurrentUser = Depends(require_permission("audits:run")),
    session: AsyncSession = Depends(get_session),
) -> AuditOut:
    if not supports_chain(payload.chain):
        raise HTTPException(status_code=400, detail=f"unsupported chain: {payload.chain}")
    address = normalise_address(payload.address) if payload.chain not in {"sol", "cosmos"} else payload.address.strip()
    service = AuditService(session)
    job = await service.enqueue(
        requested_by=user.user_id, chain=payload.chain, address=address, deep=payload.deep
    )
    return AuditOut.model_validate(job)


@router.get("", response_model=list[AuditOut])
async def list_audits(
    address: str | None = None,
    page: int = 1,
    size: int = 50,
    session: AsyncSession = Depends(get_session),
    _: CurrentUser = Depends(get_current_user),
) -> list[AuditOut]:
    repo = AuditRepository(session)
    items = await repo.list(limit=size, offset=(page - 1) * size, address=address)
    return [AuditOut.model_validate(j) for j in items]


@router.get("/{audit_id}", response_model=AuditOut)
async def get_audit(
    audit_id: str,
    session: AsyncSession = Depends(get_session),
    _: CurrentUser = Depends(get_current_user),
) -> AuditOut:
    repo = AuditRepository(session)
    job = await repo.get(audit_id)
    if job is None:
        raise HTTPException(status_code=404, detail="audit not found")
    return AuditOut.model_validate(job)
