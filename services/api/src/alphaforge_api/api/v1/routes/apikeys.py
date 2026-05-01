from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from alphaforge_api.core.database import get_session
from alphaforge_api.core.security import CurrentUser, generate_api_key, get_current_user
from alphaforge_api.repositories.user import APIKeyRepository
from alphaforge_api.schemas.user import APIKeyCreate, APIKeyCreated, APIKeyOut

router = APIRouter(prefix="/apikeys")


@router.post("", response_model=APIKeyCreated, status_code=201)
async def create(
    payload: APIKeyCreate,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> APIKeyCreated:
    repo = APIKeyRepository(session)
    plaintext, hashed = generate_api_key()
    record = await repo.create(
        user_id=user.user_id,
        label=payload.label,
        key_hash=hashed,
        scopes=payload.scopes,
        expires_at=payload.expires_at,
    )
    out = APIKeyOut.model_validate(record).model_dump()
    out["plaintext"] = plaintext
    return APIKeyCreated.model_validate(out)


@router.get("", response_model=list[APIKeyOut])
async def list_keys(
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[APIKeyOut]:
    repo = APIKeyRepository(session)
    keys = await repo.list_for_user(user.user_id)
    return [APIKeyOut.model_validate(k) for k in keys]


@router.delete("/{key_id}", status_code=204)
async def revoke(
    key_id: str,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> None:
    repo = APIKeyRepository(session)
    keys = await repo.list_for_user(user.user_id)
    target = next((k for k in keys if k.id == key_id), None)
    if target is None:
        raise HTTPException(status_code=404, detail="key not found")
    await repo.revoke(target)
