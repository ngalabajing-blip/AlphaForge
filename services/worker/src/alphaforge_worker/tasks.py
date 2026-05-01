"""Top-level Celery tasks."""
from __future__ import annotations

from datetime import datetime, timezone

from alphaforge_worker.celery_app import celery_app
from alphaforge_worker.runtime.backtest_runner import BacktestRunner
from alphaforge_worker.runtime.live_runner import LiveStrategyRunner
from alphaforge_shared.logging import get_logger

log = get_logger("alphaforge_worker.tasks")


@celery_app.task(name="alphaforge_worker.run_backtest", bind=True, max_retries=2,
                 default_retry_delay=10)
def run_backtest(self, backtest_id: str) -> dict:
    log.info("celery_run_backtest", backtest_id=backtest_id)
    runner = BacktestRunner()
    summary = runner.run(backtest_id)
    return summary


@celery_app.task(name="alphaforge_worker.run_strategy_live", bind=True)
def run_strategy_live(self, strategy_id: str, version: int | None = None) -> dict:
    log.info("celery_run_live", strategy_id=strategy_id, version=version)
    runner = LiveStrategyRunner()
    return runner.run(strategy_id=strategy_id, version=version)


@celery_app.task(name="alphaforge_worker.health")
def health() -> dict:
    return {"ok": True, "ts": datetime.now(tz=timezone.utc).isoformat()}
