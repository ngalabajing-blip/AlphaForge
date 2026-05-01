from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from alphaforge_api.models.user import APIKey, User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, user_id: str) -> Optional[User]:
        return await self.session.get(User, user_id)

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email.lower())
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def create(self, **kwargs: object) -> User:
        if "email" in kwargs and isinstance(kwargs["email"], str):
            kwargs["email"] = kwargs["email"].lower()
        user = User(**kwargs)
        self.session.add(user)
        await self.session.flush()
        return user

    async def touch_login(self, user: User) -> None:
        user.last_login_at = datetime.now(tz=timezone.utc)
        await self.session.flush()

    async def list(self, *, limit: int = 50, offset: int = 0) -> list[User]:
        stmt = select(User).order_by(User.created_at.desc()).limit(limit).offset(offset)
        return list((await self.session.execute(stmt)).scalars().all())

    async def count(self) -> int:
        from sqlalchemy import func
        stmt = select(func.count()).select_from(User)
        return int((await self.session.execute(stmt)).scalar() or 0)


class APIKeyRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, *, user_id: str, label: str, key_hash: str, scopes: list[str],
                     expires_at: Optional[datetime] = None) -> APIKey:
        key = APIKey(
            user_id=user_id,
            label=label,
            key_hash=key_hash,
            scopes=scopes,
            expires_at=expires_at,
        )
        self.session.add(key)
        await self.session.flush()
        return key

    async def get_by_hash(self, key_hash: str) -> Optional[APIKey]:
        stmt = select(APIKey).where(APIKey.key_hash == key_hash, APIKey.revoked_at.is_(None))
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def list_for_user(self, user_id: str) -> list[APIKey]:
        stmt = select(APIKey).where(APIKey.user_id == user_id).order_by(APIKey.created_at.desc())
        return list((await self.session.execute(stmt)).scalars().all())

    async def revoke(self, api_key: APIKey) -> APIKey:
        api_key.revoked_at = datetime.now(tz=timezone.utc)
        await self.session.flush()
        return api_key

    async def touch(self, api_key: APIKey) -> None:
        api_key.last_used_at = datetime.now(tz=timezone.utc)
        await self.session.flush()
