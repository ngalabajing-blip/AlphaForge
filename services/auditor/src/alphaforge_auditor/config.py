from __future__ import annotations

from functools import lru_cache

from alphaforge_shared.settings import CommonSettings
from pydantic import Field


class AuditorSettings(CommonSettings):
    etherscan_api_key: str | None = Field(default=None, alias="ETHERSCAN_API_KEY")
    bscscan_api_key: str | None = Field(default=None, alias="BSCSCAN_API_KEY")
    polygonscan_api_key: str | None = Field(default=None, alias="POLYGONSCAN_API_KEY")
    arbiscan_api_key: str | None = Field(default=None, alias="ARBISCAN_API_KEY")
    basescan_api_key: str | None = Field(default=None, alias="BASESCAN_API_KEY")
    optimism_api_key: str | None = Field(default=None, alias="OPTIMISTIC_ETHERSCAN_API_KEY")
    snowtrace_api_key: str | None = Field(default=None, alias="SNOWTRACE_API_KEY")
    deep_max_seconds: int = Field(default=120, alias="AUDITOR_DEEP_MAX_SECONDS")


@lru_cache(maxsize=1)
def get_settings() -> AuditorSettings:
    return AuditorSettings()
