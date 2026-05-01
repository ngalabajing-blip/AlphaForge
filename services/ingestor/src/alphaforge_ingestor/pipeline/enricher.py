"""Optional enrichment helpers (token metadata caching)."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Optional


@dataclass
class TokenMetadata:
    address: str
    symbol: str
    name: str
    decimals: int


class TokenMetadataCache:
    """Tiny LRU-ish cache keyed by ``chain:address``."""

    def __init__(self, *, max_size: int = 4096) -> None:
        self.max_size = max_size
        self._data: dict[str, TokenMetadata] = {}
        self._lock = asyncio.Lock()

    async def get(self, chain: str, address: str) -> Optional[TokenMetadata]:
        async with self._lock:
            return self._data.get(f"{chain}:{address.lower()}")

    async def set(self, meta: TokenMetadata, chain: str) -> None:
        key = f"{chain}:{meta.address.lower()}"
        async with self._lock:
            self._data[key] = meta
            if len(self._data) > self.max_size:
                # drop oldest 10% (insertion-ordered dict)
                drop = max(1, self.max_size // 10)
                for old_key in list(self._data.keys())[:drop]:
                    self._data.pop(old_key, None)
