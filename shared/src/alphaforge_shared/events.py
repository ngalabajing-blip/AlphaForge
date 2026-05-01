"""
Pydantic event schemas for the Kafka bus.

All events extend :class:`BaseEvent`, which carries a stable envelope:

  * ``event_id``  — UUIDv7-ish id (sortable)
  * ``ts``        — ISO-8601 timestamp (UTC)
  * ``producer``  — service that emitted the event
  * ``schema``    — fully qualified topic name + version
  * ``trace_id``  — OpenTelemetry trace id, if available
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Annotated, Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _now() -> datetime:
    return datetime.now(tz=timezone.utc)


def _new_id() -> str:
    return uuid.uuid4().hex


class EventSeverity(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class BaseEvent(BaseModel):
    """Common envelope for every Kafka payload."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    event_id: str = Field(default_factory=_new_id)
    ts: datetime = Field(default_factory=_now)
    producer: str
    schema: str
    trace_id: Optional[str] = None


# ── Chain ingestion ────────────────────────────────────────────────────────────
class BlockEvent(BaseEvent):
    schema: Literal["af.chain.block.v1"] = "af.chain.block.v1"
    chain: str
    height: int
    block_hash: str
    parent_hash: str
    tx_count: int
    gas_used: Optional[int] = None
    gas_limit: Optional[int] = None
    miner: Optional[str] = None


class TransactionEvent(BaseEvent):
    schema: Literal["af.chain.tx.v1"] = "af.chain.tx.v1"
    chain: str
    block_height: int
    tx_hash: str
    sender: str
    recipient: Optional[str]
    value_native: Decimal
    gas_price: Optional[Decimal] = None
    gas_used: Optional[int] = None
    success: bool = True
    method_id: Optional[str] = None  # 4-byte selector for EVM
    raw_input: Optional[str] = None

    @field_validator("value_native", mode="before")
    @classmethod
    def _to_decimal(cls, v: Any) -> Decimal:
        return v if isinstance(v, Decimal) else Decimal(str(v))


class LogEvent(BaseEvent):
    schema: Literal["af.chain.log.v1"] = "af.chain.log.v1"
    chain: str
    tx_hash: str
    log_index: int
    address: str
    topics: list[str]
    data: str
    decoded_event: Optional[str] = None
    decoded_args: Optional[dict[str, Any]] = None


# ── Market ─────────────────────────────────────────────────────────────────────
class PriceEvent(BaseEvent):
    schema: Literal["af.market.price.v1"] = "af.market.price.v1"
    source: str                      # "coingecko", "defillama", "uniswap", …
    chain: Optional[str]
    symbol: str
    address: Optional[str]           # token contract / mint
    price_usd: Decimal
    market_cap: Optional[Decimal] = None
    volume_24h: Optional[Decimal] = None
    change_24h: Optional[Decimal] = None


class DexTradeEvent(BaseEvent):
    schema: Literal["af.market.trade.v1"] = "af.market.trade.v1"
    chain: str
    venue: str                       # "uniswap-v3", "raydium", …
    pool: str
    base_symbol: str
    quote_symbol: str
    base_amount: Decimal
    quote_amount: Decimal
    price: Decimal
    side: Literal["buy", "sell"]
    trader: str
    tx_hash: str


class LiquidityEvent(BaseEvent):
    schema: Literal["af.market.liquidity.v1"] = "af.market.liquidity.v1"
    chain: str
    venue: str
    pool: str
    operation: Literal["add", "remove"]
    base_amount: Decimal
    quote_amount: Decimal
    provider: str
    tx_hash: str


# ── ML ─────────────────────────────────────────────────────────────────────────
class AnomalyEvent(BaseEvent):
    schema: Literal["af.ml.anomaly.v1"] = "af.ml.anomaly.v1"
    chain: Optional[str]
    subject_type: Literal["address", "pool", "token", "tx"]
    subject: str
    score: float
    threshold: float
    label: Literal["normal", "suspicious", "anomalous"]
    severity: EventSeverity
    explanation: str
    feature_snapshot: dict[str, float] = Field(default_factory=dict)


class SentimentEvent(BaseEvent):
    schema: Literal["af.ml.sentiment.v1"] = "af.ml.sentiment.v1"
    source: str                      # "twitter", "reddit", "telegram", "news"
    symbol: Optional[str]
    address: Optional[str]
    score: float                     # -1 (bearish) … +1 (bullish)
    magnitude: float                 # 0 … 1
    text_excerpt: str


class PricePredictionEvent(BaseEvent):
    schema: Literal["af.ml.prediction.v1"] = "af.ml.prediction.v1"
    symbol: str
    horizon_minutes: int
    predicted_price: Decimal
    confidence: float
    model: str


# ── Strategy ───────────────────────────────────────────────────────────────────
class SignalAction(str, Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    CLOSE = "close"
    REBALANCE = "rebalance"


class SignalEvent(BaseEvent):
    schema: Literal["af.strategy.signal.v1"] = "af.strategy.signal.v1"
    strategy_id: str
    run_id: str
    symbol: str
    action: SignalAction
    strength: float                  # 0 … 1
    suggested_size: Optional[Decimal] = None
    reasons: list[str] = Field(default_factory=list)
    indicators: dict[str, float] = Field(default_factory=dict)


class OrderEvent(BaseEvent):
    schema: Literal["af.strategy.order.v1"] = "af.strategy.order.v1"
    strategy_id: str
    run_id: str
    order_id: str
    symbol: str
    side: Literal["buy", "sell"]
    quantity: Decimal
    price: Optional[Decimal]
    order_type: Literal["market", "limit", "stop", "stop-limit"]
    venue: str = "paper"


class FillEvent(BaseEvent):
    schema: Literal["af.strategy.fill.v1"] = "af.strategy.fill.v1"
    order_id: str
    strategy_id: str
    run_id: str
    symbol: str
    side: Literal["buy", "sell"]
    quantity: Decimal
    price: Decimal
    fees: Decimal = Decimal("0")
    realized_pnl: Optional[Decimal] = None


# ── Alerts / Audit ─────────────────────────────────────────────────────────────
class AlertEvent(BaseEvent):
    schema: Literal["af.alert.fired.v1"] = "af.alert.fired.v1"
    alert_id: str
    user_id: str
    title: str
    body: str
    severity: EventSeverity
    channels: list[str]              # ["telegram", "email", …]
    metadata: dict[str, Any] = Field(default_factory=dict)


class NotificationResult(BaseEvent):
    schema: Literal["af.notification.result.v1"] = "af.notification.result.v1"
    alert_id: str
    channel: str
    success: bool
    error: Optional[str] = None
    delivered_at: datetime = Field(default_factory=_now)


class AuditRequest(BaseEvent):
    schema: Literal["af.audit.requested.v1"] = "af.audit.requested.v1"
    audit_id: str
    chain: str
    address: str
    deep: bool = True
    requested_by: Optional[str] = None


class AuditFinding(BaseModel):
    rule: str
    severity: EventSeverity
    title: str
    description: str
    location: Optional[str] = None   # file:line or bytecode offset
    evidence: Optional[str] = None
    cwe: Optional[str] = None
    swc: Optional[str] = None


class AuditReport(BaseEvent):
    schema: Literal["af.audit.report.v1"] = "af.audit.report.v1"
    audit_id: str
    chain: str
    address: str
    overall_score: float
    risk_level: EventSeverity
    findings: list[AuditFinding]
    bytecode_size: int
    has_source: bool
    summary: str


__all__ = [name for name in dict(globals()) if name.endswith(("Event", "Result", "Request", "Report", "Finding"))]
__all__.extend(["BaseEvent", "EventSeverity", "SignalAction"])
