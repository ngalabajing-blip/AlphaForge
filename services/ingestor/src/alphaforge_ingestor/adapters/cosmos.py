"""Cosmos / Tendermint adapter (HTTP-only, minimal)."""

from __future__ import annotations

import asyncio
import os

import httpx
from alphaforge_shared.events import BlockEvent
from alphaforge_shared.logging import get_logger
from alphaforge_shared.topics import T_BLOCKS

from alphaforge_ingestor.adapters.base import ChainAdapter
from alphaforge_ingestor.config import get_settings
from alphaforge_ingestor.kafka_sink import KafkaSink

log = get_logger("alphaforge_ingestor.cosmos")


class CosmosAdapter(ChainAdapter):
    def __init__(self, spec) -> None:  # type: ignore[no-untyped-def]
        super().__init__(spec)
        self._http: httpx.AsyncClient | None = None

    async def run(self, sink: KafkaSink) -> None:
        url = os.getenv(self.spec.rpc_http_env)
        if not url:
            log.warning("cosmos_no_rpc", chain=self.spec.id)
            return
        self._http = httpx.AsyncClient(base_url=url, timeout=15.0)
        settings = get_settings()
        last_height: int | None = None
        while True:
            try:
                resp = await self._http.get("/status")
                resp.raise_for_status()
                data = resp.json()
                height = int(data["result"]["sync_info"]["latest_block_height"])
                if last_height is not None and height <= last_height:
                    await asyncio.sleep(settings.poll_interval_seconds)
                    continue
                be = BlockEvent(
                    producer="alphaforge-ingestor",
                    chain=self.spec.id,
                    height=height,
                    block_hash=data["result"]["sync_info"]["latest_block_hash"],
                    parent_hash="",
                    tx_count=0,
                )
                await sink.publish(T_BLOCKS, be, key=self.spec.id, chain=self.spec.id)
                last_height = height
            except asyncio.CancelledError:
                raise
            except Exception:  # noqa: BLE001
                log.exception("cosmos_poll_failed", chain=self.spec.id)
            await asyncio.sleep(settings.poll_interval_seconds)

    async def aclose(self) -> None:
        if self._http is not None:
            await self._http.aclose()
            self._http = None
