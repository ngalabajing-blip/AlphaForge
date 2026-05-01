"""
EVM adapter — subscribes to ``newHeads`` over WebSocket if available, and
falls back to HTTP polling. Decodes a curated subset of ERC-20 / Uniswap V2
events from logs.
"""
from __future__ import annotations

import asyncio
import json
import os
from decimal import Decimal
from typing import Any, AsyncIterator

import httpx
from tenacity import AsyncRetrying, stop_after_attempt, wait_exponential

from alphaforge_ingestor.adapters.base import ChainAdapter
from alphaforge_ingestor.config import get_settings
from alphaforge_ingestor.kafka_sink import KafkaSink
from alphaforge_ingestor.pipeline.decoder import EVMLogDecoder
from alphaforge_shared.events import BlockEvent, LogEvent, TransactionEvent
from alphaforge_shared.logging import get_logger
from alphaforge_shared.topics import T_BLOCKS, T_LOGS, T_TRANSACTIONS

log = get_logger("alphaforge_ingestor.evm")


class EVMAdapter(ChainAdapter):
    def __init__(self, spec) -> None:  # type: ignore[no-untyped-def]
        super().__init__(spec)
        self._http: httpx.AsyncClient | None = None
        self._decoder = EVMLogDecoder()

    async def run(self, sink: KafkaSink) -> None:
        rpc_http = os.getenv(self.spec.rpc_http_env)
        if not rpc_http:
            log.warning("evm_no_rpc_http", chain=self.spec.id, env=self.spec.rpc_http_env)
            return
        self._http = httpx.AsyncClient(base_url=rpc_http, timeout=15.0, headers={"Content-Type": "application/json"})
        ws_url = os.getenv(self.spec.rpc_ws_env)
        if ws_url:
            try:
                await self._run_ws(ws_url, sink)
                return
            except Exception:  # noqa: BLE001
                log.exception("evm_ws_failed_fallback_to_polling", chain=self.spec.id)
        await self._run_polling(sink)

    async def aclose(self) -> None:
        if self._http is not None:
            await self._http.aclose()
            self._http = None

    # ── websocket subscription ────────────────────────────────────────────────
    async def _run_ws(self, ws_url: str, sink: KafkaSink) -> None:
        import websockets  # local import keeps optional dep optional

        log.info("evm_ws_connect", chain=self.spec.id, url=_redact(ws_url))
        async with websockets.connect(ws_url, ping_interval=15, ping_timeout=15) as ws:
            await ws.send(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_subscribe",
                                     "params": ["newHeads"]}))
            ack = await ws.recv()
            log.debug("evm_ws_subscribed", chain=self.spec.id, ack=ack)
            while True:
                raw = await ws.recv()
                try:
                    payload = json.loads(raw)
                    head = payload.get("params", {}).get("result")
                    if head is None:
                        continue
                    height = int(head["number"], 16)
                    block = await self._fetch_block(height)
                    if block is None:
                        continue
                    await self._emit_block(block, sink)
                except Exception:  # noqa: BLE001
                    log.exception("evm_ws_parse_failed", chain=self.spec.id)

    # ── polling fallback ──────────────────────────────────────────────────────
    async def _run_polling(self, sink: KafkaSink) -> None:
        settings = get_settings()
        last_height: int | None = None
        while True:
            try:
                tip = await self._latest_height()
                if tip is None:
                    await asyncio.sleep(settings.poll_interval_seconds)
                    continue
                start_h = max(last_height + 1 if last_height else tip - 1,
                              tip - settings.max_block_lookback)
                for h in range(start_h, tip + 1):
                    block = await self._fetch_block(h)
                    if block is not None:
                        await self._emit_block(block, sink)
                last_height = tip
            except asyncio.CancelledError:
                raise
            except Exception:  # noqa: BLE001
                log.exception("evm_poll_failed", chain=self.spec.id)
            await asyncio.sleep(settings.poll_interval_seconds)

    # ── RPC helpers ───────────────────────────────────────────────────────────
    async def _rpc(self, method: str, params: list[Any] | None = None) -> Any:
        assert self._http is not None
        payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params or []}
        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(3),
            wait=wait_exponential(min=0.25, max=4.0),
            reraise=True,
        ):
            with attempt:
                resp = await self._http.post("", json=payload)
                resp.raise_for_status()
                data = resp.json()
                if "error" in data:
                    raise RuntimeError(data["error"])
                return data["result"]

    async def _latest_height(self) -> int | None:
        try:
            result = await self._rpc("eth_blockNumber")
            return int(result, 16)
        except Exception:
            return None

    async def _fetch_block(self, height: int) -> dict | None:
        try:
            return await self._rpc("eth_getBlockByNumber", [hex(height), True])
        except Exception:
            return None

    # ── emission ──────────────────────────────────────────────────────────────
    async def _emit_block(self, block: dict, sink: KafkaSink) -> None:
        height = int(block["number"], 16)
        block_event = BlockEvent(
            producer="alphaforge-ingestor",
            chain=self.spec.id,
            height=height,
            block_hash=block["hash"],
            parent_hash=block["parentHash"],
            tx_count=len(block.get("transactions", [])),
            gas_used=int(block.get("gasUsed", "0x0"), 16),
            gas_limit=int(block.get("gasLimit", "0x0"), 16),
            miner=block.get("miner"),
        )
        await sink.publish(T_BLOCKS, block_event, key=self.spec.id, chain=self.spec.id)

        for tx in block.get("transactions", []):
            try:
                ev = TransactionEvent(
                    producer="alphaforge-ingestor",
                    chain=self.spec.id,
                    block_height=height,
                    tx_hash=tx["hash"],
                    sender=tx["from"],
                    recipient=tx.get("to"),
                    value_native=Decimal(int(tx.get("value", "0x0"), 16)) / Decimal(10 ** 18),
                    gas_price=Decimal(int(tx.get("gasPrice", "0x0"), 16)) if "gasPrice" in tx else None,
                    method_id=tx.get("input", "0x")[:10] if tx.get("input", "0x") != "0x" else None,
                )
                await sink.publish(T_TRANSACTIONS, ev, key=tx["hash"], chain=self.spec.id)
            except Exception:  # noqa: BLE001
                log.exception("evm_tx_emit_failed", chain=self.spec.id, tx=tx.get("hash"))

        # logs (best-effort: a few popular events at the block scope)
        try:
            logs = await self._rpc(
                "eth_getLogs",
                [{"fromBlock": hex(height), "toBlock": hex(height)}],
            )
        except Exception:
            logs = []
        for entry in logs:
            try:
                decoded_event, decoded_args = self._decoder.try_decode(entry)
                ev = LogEvent(
                    producer="alphaforge-ingestor",
                    chain=self.spec.id,
                    tx_hash=entry["transactionHash"],
                    log_index=int(entry.get("logIndex", "0x0"), 16),
                    address=entry["address"],
                    topics=entry.get("topics", []),
                    data=entry.get("data", "0x"),
                    decoded_event=decoded_event,
                    decoded_args=decoded_args,
                )
                await sink.publish(T_LOGS, ev, key=entry.get("address"), chain=self.spec.id)
            except Exception:  # noqa: BLE001
                log.exception("evm_log_emit_failed", chain=self.spec.id)


def _redact(url: str) -> str:
    if "?" in url:
        return url.split("?", 1)[0] + "?…"
    return url
