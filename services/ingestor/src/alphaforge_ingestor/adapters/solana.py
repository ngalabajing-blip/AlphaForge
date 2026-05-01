"""Solana adapter — uses HTTP getSlot + getBlock polling, optional WebSocket."""

from __future__ import annotations

import asyncio
import os
from decimal import Decimal
from typing import Any

import httpx
from alphaforge_shared.events import BlockEvent, TransactionEvent
from alphaforge_shared.logging import get_logger
from alphaforge_shared.topics import T_BLOCKS, T_TRANSACTIONS

from alphaforge_ingestor.adapters.base import ChainAdapter
from alphaforge_ingestor.config import get_settings
from alphaforge_ingestor.kafka_sink import KafkaSink

log = get_logger("alphaforge_ingestor.sol")


class SolanaAdapter(ChainAdapter):
    def __init__(self, spec) -> None:  # type: ignore[no-untyped-def]
        super().__init__(spec)
        self._http: httpx.AsyncClient | None = None

    async def run(self, sink: KafkaSink) -> None:
        url = os.getenv(self.spec.rpc_http_env)
        if not url:
            log.warning("sol_no_rpc", chain=self.spec.id)
            return
        self._http = httpx.AsyncClient(
            base_url=url, timeout=15.0, headers={"Content-Type": "application/json"}
        )
        settings = get_settings()
        last_slot: int | None = None
        while True:
            try:
                slot = await self._rpc("getSlot")
                if not isinstance(slot, int):
                    await asyncio.sleep(settings.poll_interval_seconds)
                    continue
                start = (last_slot + 1) if last_slot is not None else slot - 1
                for s in range(max(start, slot - settings.max_block_lookback), slot + 1):
                    await self._fetch_and_emit(s, sink)
                last_slot = slot
            except asyncio.CancelledError:
                raise
            except Exception:  # noqa: BLE001
                log.exception("sol_poll_failed", chain=self.spec.id)
            await asyncio.sleep(settings.poll_interval_seconds)

    async def aclose(self) -> None:
        if self._http is not None:
            await self._http.aclose()
            self._http = None

    async def _rpc(self, method: str, params: list[Any] | None = None) -> Any:
        assert self._http is not None
        try:
            resp = await self._http.post(
                "",
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": method,
                    "params": params or [],
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("result")
        except Exception:
            return None

    async def _fetch_and_emit(self, slot: int, sink: KafkaSink) -> None:
        block = await self._rpc(
            "getBlock",
            [
                slot,
                {
                    "transactionDetails": "signatures",
                    "rewards": False,
                    "maxSupportedTransactionVersion": 0,
                },
            ],
        )
        if not isinstance(block, dict):
            return
        be = BlockEvent(
            producer="alphaforge-ingestor",
            chain=self.spec.id,
            height=slot,
            block_hash=block.get("blockhash", ""),
            parent_hash=block.get("previousBlockhash", ""),
            tx_count=(len(block.get("signatures", [])) if isinstance(block.get("signatures"), list) else 0),
        )
        await sink.publish(T_BLOCKS, be, key=self.spec.id, chain=self.spec.id)
        # signatures only — the worker can request full tx detail if needed.
        for sig in block.get("signatures", []) or []:
            try:
                te = TransactionEvent(
                    producer="alphaforge-ingestor",
                    chain=self.spec.id,
                    block_height=slot,
                    tx_hash=sig,
                    sender="",
                    recipient=None,
                    value_native=Decimal("0"),
                )
                await sink.publish(T_TRANSACTIONS, te, key=sig, chain=self.spec.id)
            except Exception:  # noqa: BLE001
                log.exception("sol_tx_emit_failed", chain=self.spec.id, sig=sig)
