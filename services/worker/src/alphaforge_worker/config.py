from __future__ import annotations

from functools import lru_cache

from alphaforge_shared.settings import CommonSettings
from pydantic import Field


class WorkerSettings(CommonSettings):
    concurrency: int = Field(default=4, alias="WORKER_CONCURRENCY")
    backtest_warmup: int = Field(default=200, alias="WORKER_BACKTEST_WARMUP")
    risk_max_position_pct: float = Field(default=0.5, alias="WORKER_RISK_MAX_POSITION_PCT")
    risk_max_drawdown_pct: float = Field(default=0.4, alias="WORKER_RISK_MAX_DRAWDOWN_PCT")
    indicators_use_rust: bool = Field(default=False, alias="WORKER_INDICATORS_USE_RUST")


@lru_cache(maxsize=1)
def get_settings() -> WorkerSettings:
    return WorkerSettings()
