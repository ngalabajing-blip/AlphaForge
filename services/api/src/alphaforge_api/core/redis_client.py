"""Redis async client wrapper."""
from __future__ import annotations

from typing import Any

from alphaforge_api.core.config import get_settings
from alphaforge_shared.logging import get_logger

log = get_logger("alphaforge_api.redis")


class RedisClient:
    def __init__(self) -> None:
        self._client: Any = None

    async def connect(self) -> None:
        if self._client is not None:
            return
        try:
            from redis.asyncio import Redis  # type: ignore[import-not-found]
        except ImportError:  # pragma: no cover
            log.warning("redis_async_not_installed")
            return
        self._client = Redis.from_url(get_settings().redis_url, decode_responses=True)
        try:
            await self._client.ping()
            log.info("redis_connected")
        except Exception:
            log.exception("redis_ping_failed")
            self._client = None

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None
            log.info("redis_closed")

    async def is_healthy(self) -> bool:
        if self._client is None:
            return False
        try:
            return bool(await self._client.ping())
        except Exception:
            return False

    async def get(self, key: str) -> Any:
        if self._client is None:
            return None
        return await self._client.get(key)

    async def set(self, key: str, value: str, *, ttl: int | None = None) -> None:
        if self._client is None:
            return
        await self._client.set(key, value, ex=ttl)

    async def delete(self, *keys: str) -> int:
        if self._client is None:
            return 0
        return await self._client.delete(*keys)

    async def incr(self, key: str, *, ttl: int | None = None) -> int:
        if self._client is None:
            return 0
        n = await self._client.incr(key)
        if ttl is not None and n == 1:
            await self._client.expire(key, ttl)
        return int(n)

    async def publish(self, channel: str, message: str) -> int:
        if self._client is None:
            return 0
        return await self._client.publish(channel, message)


redis_client = RedisClient()
