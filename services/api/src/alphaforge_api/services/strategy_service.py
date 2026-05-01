from __future__ import annotations

from typing import Optional

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from alphaforge_api.repositories.strategy import StrategyRepository
from alphaforge_api.schemas.strategy import StrategyCreate, StrategyUpdate
from alphaforge_api.services.dsl_loader import loads as parse_dsl
from alphaforge_shared.exceptions import StrategyParseError


class StrategyService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = StrategyRepository(session)

    async def create(self, *, owner_id: str, payload: StrategyCreate):
        try:
            dsl = parse_dsl(payload.raw_source)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=f"invalid DSL: {exc}") from exc

        strategy = await self.repo.create(
            owner_id=owner_id,
            name=payload.name,
            description=payload.description,
            is_public=payload.is_public,
            tags=payload.tags,
        )
        await self.repo.add_version(
            strategy=strategy,
            raw_source=payload.raw_source,
            dsl=dsl,
            parameters=payload.parameters,
        )
        return strategy

    async def update(self, *, strategy_id: str, owner_id: str, payload: StrategyUpdate):
        strategy = await self.repo.get_for_owner(strategy_id, owner_id)
        if strategy is None:
            raise HTTPException(status_code=404, detail="strategy not found")
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(strategy, field, value)
        await self.session.flush()
        return strategy

    async def delete(self, *, strategy_id: str, owner_id: str) -> None:
        strategy = await self.repo.get_for_owner(strategy_id, owner_id)
        if strategy is None:
            raise HTTPException(status_code=404, detail="strategy not found")
        await self.session.delete(strategy)
        await self.session.flush()

    async def add_version(
        self,
        *,
        strategy_id: str,
        owner_id: str,
        raw_source: str,
        parameters: dict,
        notes: Optional[str] = None,
    ):
        strategy = await self.repo.get_for_owner(strategy_id, owner_id)
        if strategy is None:
            raise HTTPException(status_code=404, detail="strategy not found")
        try:
            dsl = parse_dsl(raw_source)
        except ValueError as exc:
            raise StrategyParseError(str(exc)) from exc
        return await self.repo.add_version(
            strategy=strategy, raw_source=raw_source, dsl=dsl,
            parameters=parameters, notes=notes,
        )
