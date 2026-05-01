"""Live strategy runner — stub that subscribes to the signal feed."""

from __future__ import annotations

from alphaforge_shared.logging import get_logger

log = get_logger("alphaforge_worker.live")


class LiveStrategyRunner:
    def run(self, *, strategy_id: str, version: int | None = None) -> dict:
        log.info("live_strategy_invoked", strategy_id=strategy_id, version=version)
        # Real implementation: subscribe to T_PRICES + indicators, evaluate rules,
        # emit T_SIGNALS / T_ORDERS to Kafka, manage live state in Redis.
        return {"status": "not_implemented", "strategy_id": strategy_id}
