"""AlphaForge worker — Celery + DSL + backtest engine."""

__version__ = "0.1.0"

from alphaforge_worker.celery_app import celery_app  # noqa: E402,F401
from alphaforge_worker.tasks import run_backtest, run_strategy_live  # noqa: E402,F401
