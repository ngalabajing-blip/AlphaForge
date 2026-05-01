"""
Feature extractors used by anomaly detection and price prediction.

The anomaly extractor folds raw trade events into a per-window feature vector
(volume, price impact, trade-size dispersion, frequency, etc.).

The candle extractor produces a vector per candle suitable for an LSTM /
RandomForest forecaster.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from datetime import datetime
from statistics import StatisticsError, mean, pstdev


# ── trade-flow features (anomaly) ─────────────────────────────────────────────
@dataclass
class TradeWindowFeatures:
    n_trades: int
    total_volume: float
    mean_size: float
    std_size: float
    max_size: float
    buy_ratio: float
    unique_addresses: int
    price_change_pct: float
    timestamps: list[datetime] = field(default_factory=list)

    def as_vector(self) -> list[float]:
        return [
            float(self.n_trades),
            self.total_volume,
            self.mean_size,
            self.std_size,
            self.max_size,
            self.buy_ratio,
            float(self.unique_addresses),
            self.price_change_pct,
        ]


def extract_trade_window(trades: Sequence[dict]) -> TradeWindowFeatures:
    if not trades:
        return TradeWindowFeatures(0, 0.0, 0.0, 0.0, 0.0, 0.5, 0, 0.0, [])
    sizes = [float(t.get("amount_in", 0) or 0) for t in trades]
    sides = [1 if (t.get("side") or "").lower() == "buy" else 0 for t in trades]
    addrs = {t.get("buyer") or t.get("from") for t in trades if t.get("buyer") or t.get("from")}
    prices = [float(t.get("price", 0) or 0) for t in trades if t.get("price")]
    try:
        std = pstdev(sizes)
    except StatisticsError:
        std = 0.0
    price_change = 0.0
    if len(prices) >= 2 and prices[0]:
        price_change = (prices[-1] - prices[0]) / prices[0]
    return TradeWindowFeatures(
        n_trades=len(trades),
        total_volume=sum(sizes),
        mean_size=mean(sizes) if sizes else 0.0,
        std_size=std,
        max_size=max(sizes) if sizes else 0.0,
        buy_ratio=sum(sides) / len(sides) if sides else 0.5,
        unique_addresses=len(addrs),
        price_change_pct=price_change,
        timestamps=[t.get("ts") for t in trades if t.get("ts")],
    )


# ── candle features (forecaster) ──────────────────────────────────────────────
@dataclass
class CandleFeatureRow:
    ts: datetime
    o: float
    h: float
    l: float
    c: float
    v: float
    rsi: float
    sma_fast: float
    sma_slow: float
    bb_upper: float
    bb_lower: float
    momentum: float

    def as_vector(self) -> list[float]:
        return [
            self.o,
            self.h,
            self.l,
            self.c,
            self.v,
            self.rsi,
            self.sma_fast,
            self.sma_slow,
            self.bb_upper,
            self.bb_lower,
            self.momentum,
        ]


def _sma(values: list[float], window: int) -> float:
    if len(values) < window or window <= 0:
        return 0.0
    return sum(values[-window:]) / window


def _rsi(closes: list[float], period: int = 14) -> float:
    if len(closes) <= period:
        return 50.0
    gains = []
    losses = []
    for i in range(-period, 0):
        delta = closes[i] - closes[i - 1]
        if delta >= 0:
            gains.append(delta)
        else:
            losses.append(-delta)
    avg_gain = sum(gains) / period if gains else 0.0
    avg_loss = sum(losses) / period if losses else 0.0
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100.0 - (100.0 / (1 + rs))


def _bollinger(closes: list[float], window: int = 20, k: float = 2.0) -> tuple[float, float]:
    if len(closes) < window:
        return (0.0, 0.0)
    window_vals = closes[-window:]
    mu = sum(window_vals) / window
    var = sum((v - mu) ** 2 for v in window_vals) / window
    std = var**0.5
    return (mu + k * std, mu - k * std)


def extract_candle_features(
    candles: Iterable[dict], *, fast: int = 12, slow: int = 26
) -> list[CandleFeatureRow]:
    rows: list[CandleFeatureRow] = []
    closes: list[float] = []
    for c in candles:
        closes.append(float(c["close"]))
        upper, lower = _bollinger(closes)
        rows.append(
            CandleFeatureRow(
                ts=(
                    c["ts"]
                    if isinstance(c["ts"], datetime)
                    else datetime.fromisoformat(str(c["ts"]).replace("Z", "+00:00"))
                ),
                o=float(c["open"]),
                h=float(c["high"]),
                l=float(c["low"]),
                c=closes[-1],
                v=float(c.get("volume", 0)),
                rsi=_rsi(closes),
                sma_fast=_sma(closes, fast),
                sma_slow=_sma(closes, slow),
                bb_upper=upper,
                bb_lower=lower,
                momentum=closes[-1] - closes[-min(len(closes), fast)],
            )
        )
    return rows
