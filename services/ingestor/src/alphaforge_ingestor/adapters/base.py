"""Base interface for per-chain ingestion adapters."""
from __future__ import annotations

import abc

from alphaforge_ingestor.kafka_sink import KafkaSink
from alphaforge_shared.chains import ChainSpec


class ChainAdapter(abc.ABC):
    """Subclass per chain family. Lifecycle: ``run`` until error or cancellation."""

    def __init__(self, spec: ChainSpec) -> None:
        self.spec = spec

    @abc.abstractmethod
    async def run(self, sink: KafkaSink) -> None:
        """Run the ingestion loop until cancellation or unrecoverable error."""

    async def aclose(self) -> None:
        """Override to clean up open sockets / clients."""
        return None
