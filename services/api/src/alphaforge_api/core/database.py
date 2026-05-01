"""Async SQLAlchemy engine + session factory."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from alphaforge_shared.logging import get_logger
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from alphaforge_api.core.config import get_settings

log = get_logger("alphaforge_api.db")


class Database:
    def __init__(self) -> None:
        self._engine: AsyncEngine | None = None
        self._sessionmaker: async_sessionmaker[AsyncSession] | None = None

    @property
    def engine(self) -> AsyncEngine:
        if self._engine is None:
            raise RuntimeError("database not connected")
        return self._engine

    @property
    def sessionmaker(self) -> async_sessionmaker[AsyncSession]:
        if self._sessionmaker is None:
            raise RuntimeError("database not connected")
        return self._sessionmaker

    async def connect(self) -> None:
        if self._engine is not None:
            return
        settings = get_settings()
        log.info("db_connect", url=_redact(settings.database_url))
        self._engine = create_async_engine(
            settings.database_url,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=300,
        )
        self._sessionmaker = async_sessionmaker(self._engine, expire_on_commit=False, autoflush=False)

    async def disconnect(self) -> None:
        if self._engine is not None:
            await self._engine.dispose()
            self._engine = None
            self._sessionmaker = None
            log.info("db_disconnect")

    async def is_healthy(self) -> bool:
        if self._engine is None:
            return False
        try:
            async with self._engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except Exception:
            log.exception("db_health_failed")
            return False

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        async with self.sessionmaker() as sess:
            try:
                yield sess
                await sess.commit()
            except Exception:
                await sess.rollback()
                raise


def _redact(url: str) -> str:
    if "@" in url and "://" in url:
        scheme, rest = url.split("://", 1)
        creds, host = rest.rsplit("@", 1)
        return f"{scheme}://***@{host}"
    return url


db = Database()


async def get_session() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency that yields a session bound to the request lifetime."""
    async with db.session() as sess:
        yield sess
