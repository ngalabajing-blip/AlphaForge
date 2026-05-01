"""
Per-chain dispatcher.

Routes the right adapter (EVM / Solana / Cosmos) for each :class:`ChainSpec`,
manages reconnect/backoff, and forwards normalised events to the Kafka sink.
"""
from __future__ import annotations

import asyncio

from alphaforge_ingestor.adapters.base import ChainAdapter
from alphaforge_ingestor.adapters.cosmos import CosmosAdapter
from alphaforge_ingestor.adapters.evm import EVMAdapter
from alphaforge_ingestor.adapters.solana import SolanaAdapter
from alphaforge_ingestor.config import get_settings
from alphaforge_ingestor.kafka_sink import KafkaSink
from alphaforge_shared.chains import ChainFamily, ChainSpec
from alphaforge_shared.exceptions import UnsupportedChainError
from alphaforge_shared.logging import get_logger

log = get_logger("alphaforge_ingestor.dispatcher")


def adapter_for(spec: ChainSpec) -> ChainAdapter:
    if spec.family is ChainFamily.EVM:
        return EVMAdapter(spec)
    if spec.family is ChainFamily.SOLANA:
        return SolanaAdapter(spec)
    if spec.family is ChainFamily.COSMOS:
        return CosmosAdapter(spec)
    raise UnsupportedChainError(f"no adapter for family {spec.family!r}")


class ChainDispatcher:
    def __init__(self, *, sink: KafkaSink) -> None:
        self.sink = sink

    async def run_chain(self, spec: ChainSpec) -> None:
        backoff = 1.0
        max_backoff = 60.0
        settings = get_settings()
        while True:
            adapter = adapter_for(spec)
            try:
                log.info("chain_start", chain=spec.id, family=spec.family.value)
                await adapter.run(self.sink)
                log.info("chain_finished_cleanly", chain=spec.id)
                return
            except asyncio.CancelledError:
                log.info("chain_cancelled", chain=spec.id)
                await adapter.aclose()
                raise
            except Exception as exc:  # noqa: BLE001
                log.exception("chain_failed", chain=spec.id, error=str(exc))
                await adapter.aclose()
                await asyncio.sleep(backoff)
                backoff = min(max_backoff, backoff * 2)
