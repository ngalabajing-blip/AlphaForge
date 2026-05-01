"""
Canonical Kafka topic names used across AlphaForge services.

Topic naming convention: ``af.<domain>.<event>.v<version>``.

Producers and consumers MUST import these constants instead of hard-coding the
strings. Bumping a topic's schema means bumping the trailing ``.v<n>`` suffix
and adding a new constant rather than editing the existing one.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Topic:
    name: str
    description: str
    partitions: int = 6
    retention_ms: int = 7 * 24 * 60 * 60 * 1000  # 7 days


# ── Ingestion ──────────────────────────────────────────────────────────────────
T_BLOCKS = Topic("af.chain.block.v1", "New finalised blocks (per chain)", partitions=12)
T_TRANSACTIONS = Topic("af.chain.tx.v1", "Normalised transactions", partitions=24)
T_LOGS = Topic("af.chain.log.v1", "EVM logs / Solana program events", partitions=24)
T_PRICES = Topic("af.market.price.v1", "Token prices (any source)", partitions=12)
T_DEX_TRADES = Topic("af.market.trade.v1", "DEX trade events (normalised)", partitions=24)
T_TOKEN_METADATA = Topic("af.token.metadata.v1", "Token metadata (decimals, name)")
T_LIQUIDITY_DELTAS = Topic("af.market.liquidity.v1", "LP add/remove events")

# ── ML ─────────────────────────────────────────────────────────────────────────
T_FEATURES = Topic("af.ml.feature.v1", "Engineered features for inference")
T_ANOMALY = Topic("af.ml.anomaly.v1", "Anomaly scores / classifications")
T_SENTIMENT = Topic("af.ml.sentiment.v1", "Sentiment scores from social streams")
T_PRICE_PREDICTION = Topic("af.ml.prediction.v1", "Short-horizon price predictions")

# ── Strategy / signals ─────────────────────────────────────────────────────────
T_SIGNALS = Topic("af.strategy.signal.v1", "Signals emitted by strategies")
T_ORDERS = Topic("af.strategy.order.v1", "Paper orders submitted by strategies")
T_FILLS = Topic("af.strategy.fill.v1", "Order fills (paper or live)")
T_BACKTEST_PROGRESS = Topic("af.backtest.progress.v1", "Live progress of running backtests")

# ── Notifications ──────────────────────────────────────────────────────────────
T_ALERTS = Topic("af.alert.fired.v1", "Alerts ready for fan-out")
T_NOTIFICATION_RESULT = Topic("af.notification.result.v1", "Delivery results")

# ── Auditor ────────────────────────────────────────────────────────────────────
T_AUDIT_REQUESTED = Topic("af.audit.requested.v1", "New audit jobs")
T_AUDIT_REPORT = Topic("af.audit.report.v1", "Completed audit reports")


def all_topics() -> tuple[Topic, ...]:
    """Return every Topic constant declared in this module."""
    import sys

    mod = sys.modules[__name__]
    return tuple(v for v in vars(mod).values() if isinstance(v, Topic))
