from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from alphaforge_api.models.strategy import Strategy, StrategyVersion


class StrategyRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, strategy_id: str) -> Strategy | None:
        return await self.session.get(Strategy, strategy_id)

    async def get_for_owner(self, strategy_id: str, owner_id: str) -> Strategy | None:
        stmt = select(Strategy).where(Strategy.id == strategy_id, Strategy.owner_id == owner_id)
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def list(
        self,
        *,
        owner_id: str | None,
        include_public: bool = True,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Strategy]:
        stmt = select(Strategy)
        if owner_id and include_public:
            stmt = stmt.where((Strategy.owner_id == owner_id) | (Strategy.is_public.is_(True)))
        elif owner_id:
            stmt = stmt.where(Strategy.owner_id == owner_id)
        elif include_public:
            stmt = stmt.where(Strategy.is_public.is_(True))
        stmt = stmt.order_by(Strategy.updated_at.desc()).limit(limit).offset(offset)
        return list((await self.session.execute(stmt)).scalars().all())

    async def count(self, *, owner_id: str | None, include_public: bool = True) -> int:
        stmt = select(func.count()).select_from(Strategy)
        if owner_id and include_public:
            stmt = stmt.where((Strategy.owner_id == owner_id) | (Strategy.is_public.is_(True)))
        elif owner_id:
            stmt = stmt.where(Strategy.owner_id == owner_id)
        elif include_public:
            stmt = stmt.where(Strategy.is_public.is_(True))
        return int((await self.session.execute(stmt)).scalar() or 0)

    async def create(
        self,
        *,
        owner_id: str,
        name: str,
        description: str | None,
        is_public: bool,
        tags: list[str],
    ) -> Strategy:
        strategy = Strategy(
            owner_id=owner_id,
            name=name,
            description=description,
            is_public=is_public,
            tags=tags,
            latest_version=0,
        )
        self.session.add(strategy)
        await self.session.flush()
        return strategy

    async def add_version(
        self,
        *,
        strategy: Strategy,
        raw_source: str,
        dsl: dict,
        parameters: dict,
        notes: str | None = None,
    ) -> StrategyVersion:
        next_version = strategy.latest_version + 1
        version = StrategyVersion(
            strategy_id=strategy.id,
            version=next_version,
            raw_source=raw_source,
            dsl=dsl,
            parameters=parameters,
            notes=notes,
        )
        strategy.latest_version = next_version
        self.session.add(version)
        await self.session.flush()
        return version

    async def get_version(self, strategy_id: str, version: int) -> StrategyVersion | None:
        stmt = select(StrategyVersion).where(
            StrategyVersion.strategy_id == strategy_id,
            StrategyVersion.version == version,
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def list_versions(self, strategy_id: str) -> list[StrategyVersion]:
        stmt = (
            select(StrategyVersion)
            .where(StrategyVersion.strategy_id == strategy_id)
            .order_by(StrategyVersion.version.desc())
        )
        return list((await self.session.execute(stmt)).scalars().all())
