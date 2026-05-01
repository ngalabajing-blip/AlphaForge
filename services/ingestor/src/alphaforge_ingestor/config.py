from __future__ import annotations

import os
from functools import lru_cache

from alphaforge_shared.settings import CommonSettings
from pydantic import Field


class IngestorSettings(CommonSettings):
    enabled_chains: list[str] = Field(
        default_factory=lambda: [
            "eth",
            "bsc",
            "polygon",
            "arbitrum",
            "base",
            "optimism",
            "avalanche",
            "sol",
        ],
        alias="INGESTOR_ENABLED_CHAINS",
    )
    poll_interval_seconds: float = Field(2.0, alias="INGESTOR_POLL_INTERVAL")
    ws_reconnect_seconds: float = Field(5.0, alias="INGESTOR_WS_RECONNECT")
    max_block_lookback: int = Field(64, alias="INGESTOR_MAX_BLOCK_LOOKBACK")
    enable_decode: bool = Field(True, alias="INGESTOR_ENABLE_DECODE")

    def rpc_http(self, env_name: str) -> str | None:
        return os.getenv(env_name)

    def rpc_ws(self, env_name: str) -> str | None:
        return os.getenv(env_name)


@lru_cache(maxsize=1)
def get_settings() -> IngestorSettings:
    return IngestorSettings()
