"""
AlphaForge quantcore — Python facade.

When the Rust extension is built (``maturin develop``) the heavy lifting goes
through ``alphaforge_quantcore._native``. We provide pure-Python fallbacks so
unit tests + the worker service still work in development environments
without a Rust toolchain.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Iterable, Sequence

try:
    from . import _native  # type: ignore[attr-defined]
    _HAS_NATIVE = True
except ImportError:
    _native = None  # type: ignore[assignment]
    _HAS_NATIVE = False

__all__ = [
    "OrderBook",
    "Order",
    "Trade",
    "ema",
    "rsi",
    "atr",
    "vwap",
    "is_native",
]


def is_native() -> bool:
    return _HAS_NATIVE


# ── data classes ──────────────────────────────────────────────────────────────
@dataclass
class Order:
    side: str           # "buy" | "sell"
    price: float
    quantity: float
    order_id: int = 0
    ts: int = 0


@dataclass
class Trade:
    price: float
    quantity: float
    aggressor: str
    maker_id: int
    taker_id: int


# ── pure-python fallback book ─────────────────────────────────────────────────
@dataclass
class _PriceLevel:
    price: float
    orders: list[Order] = field(default_factory=list)

    def total_qty(self) -> float:
        return sum(o.quantity for o in self.orders)


class OrderBook:
    """Limit order book — Rust implementation when available."""

    def __init__(self) -> None:
        if _HAS_NATIVE:
            self._native = _native.OrderBook()  # type: ignore[union-attr]
        else:
            self._native = None
            self._bids: list[_PriceLevel] = []
            self._asks: list[_PriceLevel] = []
            self._next_id = 1

    def submit(self, side: str, price: float, quantity: float) -> list[Trade]:
        if self._native is not None:
            raw = self._native.submit(side, price, quantity)
            return [Trade(**t) for t in raw]
        side = side.lower()
        if side not in {"buy", "sell"}:
            raise ValueError("side must be buy/sell")
        order = Order(side=side, price=price, quantity=quantity, order_id=self._next_id)
        self._next_id += 1
        trades = self._match(order)
        if order.quantity > 0:
            self._rest(order)
        return trades

    def _match(self, taker: Order) -> list[Trade]:
        trades: list[Trade] = []
        book = self._asks if taker.side == "buy" else self._bids
        while taker.quantity > 0 and book:
            best = book[0]
            if (taker.side == "buy" and best.price > taker.price) or \
               (taker.side == "sell" and best.price < taker.price):
                break
            for maker in list(best.orders):
                qty = min(maker.quantity, taker.quantity)
                trades.append(Trade(
                    price=best.price, quantity=qty,
                    aggressor=taker.side, maker_id=maker.order_id, taker_id=taker.order_id,
                ))
                maker.quantity -= qty
                taker.quantity -= qty
                if maker.quantity <= 0:
                    best.orders.remove(maker)
                if taker.quantity <= 0:
                    break
            if not best.orders:
                book.pop(0)
        return trades

    def _rest(self, order: Order) -> None:
        book = self._bids if order.side == "buy" else self._asks
        for level in book:
            if level.price == order.price:
                level.orders.append(order)
                return
        book.append(_PriceLevel(price=order.price, orders=[order]))
        # bids descending, asks ascending
        if order.side == "buy":
            book.sort(key=lambda lv: -lv.price)
        else:
            book.sort(key=lambda lv: lv.price)

    def best_bid(self) -> float:
        if self._native is not None:
            return float(self._native.best_bid())
        return self._bids[0].price if self._bids else 0.0

    def best_ask(self) -> float:
        if self._native is not None:
            return float(self._native.best_ask())
        return self._asks[0].price if self._asks else 0.0

    def depth(self, levels: int = 10) -> dict[str, list[tuple[float, float]]]:
        if self._native is not None:
            return self._native.depth(levels)
        return {
            "bids": [(lv.price, lv.total_qty()) for lv in self._bids[:levels]],
            "asks": [(lv.price, lv.total_qty()) for lv in self._asks[:levels]],
        }


# ── pure-python indicator fallbacks ───────────────────────────────────────────
def ema(values: Sequence[float], period: int) -> list[float]:
    if _HAS_NATIVE:
        return list(_native.ema(list(values), period))  # type: ignore[union-attr]
    if not values:
        return []
    alpha = 2.0 / (period + 1)
    out: list[float] = []
    prev = values[0]
    for v in values:
        prev = prev + alpha * (v - prev)
        out.append(prev)
    return out


def rsi(values: Sequence[float], period: int = 14) -> list[float]:
    if _HAS_NATIVE:
        return list(_native.rsi(list(values), period))  # type: ignore[union-attr]
    if len(values) < period + 1:
        return [50.0] * len(values)
    gains = [0.0]
    losses = [0.0]
    for i in range(1, len(values)):
        d = values[i] - values[i - 1]
        gains.append(max(d, 0.0))
        losses.append(max(-d, 0.0))
    out = [50.0] * len(values)
    for i in range(period, len(values)):
        avg_g = sum(gains[i - period + 1:i + 1]) / period
        avg_l = sum(losses[i - period + 1:i + 1]) / period
        if avg_l == 0:
            out[i] = 100.0
        else:
            rs = avg_g / avg_l
            out[i] = 100.0 - 100.0 / (1.0 + rs)
    return out


def atr(highs: Sequence[float], lows: Sequence[float], closes: Sequence[float], period: int = 14) -> list[float]:
    if _HAS_NATIVE:
        return list(_native.atr(list(highs), list(lows), list(closes), period))  # type: ignore[union-attr]
    n = len(closes)
    if n == 0:
        return []
    trs: list[float] = []
    for i in range(n):
        if i == 0:
            trs.append(highs[i] - lows[i])
        else:
            trs.append(max(
                highs[i] - lows[i],
                abs(highs[i] - closes[i - 1]),
                abs(lows[i] - closes[i - 1]),
            ))
    out: list[float] = []
    for i in range(n):
        if i < period:
            out.append(sum(trs[: i + 1]) / (i + 1))
        else:
            out.append(sum(trs[i - period + 1: i + 1]) / period)
    return out


def vwap(prices: Sequence[float], volumes: Sequence[float]) -> list[float]:
    if _HAS_NATIVE:
        return list(_native.vwap(list(prices), list(volumes)))  # type: ignore[union-attr]
    cum_pv = 0.0
    cum_v = 0.0
    out: list[float] = []
    for p, v in zip(prices, volumes):
        cum_pv += p * v
        cum_v += v
        out.append(cum_pv / cum_v if cum_v else p)
    return out
