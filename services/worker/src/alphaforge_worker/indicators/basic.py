"""Basic technical indicators implemented in pure Python."""
from __future__ import annotations

from collections import deque
from typing import Any, Deque

from alphaforge_worker.indicators.registry import Indicator, register_indicator


@register_indicator("sma")
class SMA(Indicator):
    def __init__(self, period: int = 20, source: str = "close") -> None:
        self.period = period
        self.source = source
        self._buffer: Deque[float] = deque(maxlen=period)
        self._values: list[float] = []

    def update(self, candle: dict) -> float:
        self._buffer.append(float(candle[self.source]))
        if len(self._buffer) < self.period:
            self._values.append(0.0)
        else:
            self._values.append(sum(self._buffer) / self.period)
        return self._values[-1]

    def latest(self) -> float:
        return self._values[-1] if self._values else 0.0


@register_indicator("ema")
class EMA(Indicator):
    def __init__(self, period: int = 20, source: str = "close") -> None:
        self.period = period
        self.source = source
        self.alpha = 2.0 / (period + 1)
        self._values: list[float] = []

    def update(self, candle: dict) -> float:
        v = float(candle[self.source])
        if not self._values:
            self._values.append(v)
        else:
            prev = self._values[-1]
            self._values.append(prev + self.alpha * (v - prev))
        return self._values[-1]

    def latest(self) -> float:
        return self._values[-1] if self._values else 0.0


@register_indicator("rsi")
class RSI(Indicator):
    def __init__(self, period: int = 14, source: str = "close") -> None:
        self.period = period
        self.source = source
        self._gains: Deque[float] = deque(maxlen=period)
        self._losses: Deque[float] = deque(maxlen=period)
        self._prev: float | None = None
        self._values: list[float] = []

    def update(self, candle: dict) -> float:
        v = float(candle[self.source])
        if self._prev is None:
            self._prev = v
            self._values.append(50.0)
            return 50.0
        delta = v - self._prev
        self._prev = v
        self._gains.append(max(delta, 0.0))
        self._losses.append(max(-delta, 0.0))
        if len(self._gains) < self.period:
            self._values.append(50.0)
            return 50.0
        avg_gain = sum(self._gains) / self.period
        avg_loss = sum(self._losses) / self.period
        if avg_loss == 0:
            self._values.append(100.0)
            return 100.0
        rs = avg_gain / avg_loss
        rsi = 100.0 - (100.0 / (1.0 + rs))
        self._values.append(rsi)
        return rsi

    def latest(self) -> float:
        return self._values[-1] if self._values else 50.0


@register_indicator("macd")
class MACD(Indicator):
    def __init__(self, fast: int = 12, slow: int = 26, signal: int = 9, source: str = "close") -> None:
        self.fast = EMA(fast, source)
        self.slow = EMA(slow, source)
        self.signal = EMA(signal, source="_macd")
        self._values: list[float] = []
        self._signal_values: list[float] = []
        self._hist: list[float] = []

    def update(self, candle: dict) -> dict[str, float]:
        f = self.fast.update(candle)
        s = self.slow.update(candle)
        macd = f - s
        self._values.append(macd)
        sig = self.signal.update({"_macd": macd})
        self._signal_values.append(sig)
        hist = macd - sig
        self._hist.append(hist)
        return {"macd": macd, "signal": sig, "hist": hist}

    def latest(self) -> dict[str, float]:
        return {
            "macd": self._values[-1] if self._values else 0.0,
            "signal": self._signal_values[-1] if self._signal_values else 0.0,
            "hist": self._hist[-1] if self._hist else 0.0,
        }


@register_indicator("atr")
class ATR(Indicator):
    def __init__(self, period: int = 14) -> None:
        self.period = period
        self._buffer: Deque[float] = deque(maxlen=period)
        self._prev_close: float | None = None
        self._values: list[float] = []

    def update(self, candle: dict) -> float:
        h = float(candle["high"])
        l = float(candle["low"])
        c = float(candle["close"])
        if self._prev_close is None:
            tr = h - l
        else:
            tr = max(h - l, abs(h - self._prev_close), abs(l - self._prev_close))
        self._prev_close = c
        self._buffer.append(tr)
        atr = sum(self._buffer) / len(self._buffer)
        self._values.append(atr)
        return atr

    def latest(self) -> float:
        return self._values[-1] if self._values else 0.0


@register_indicator("bollinger")
class Bollinger(Indicator):
    def __init__(self, period: int = 20, k: float = 2.0, source: str = "close") -> None:
        self.period = period
        self.k = k
        self.source = source
        self._buffer: Deque[float] = deque(maxlen=period)
        self._upper: list[float] = []
        self._lower: list[float] = []
        self._mid: list[float] = []

    def update(self, candle: dict) -> dict[str, float]:
        v = float(candle[self.source])
        self._buffer.append(v)
        if len(self._buffer) < self.period:
            self._upper.append(v)
            self._lower.append(v)
            self._mid.append(v)
            return {"upper": v, "mid": v, "lower": v}
        mu = sum(self._buffer) / self.period
        var = sum((x - mu) ** 2 for x in self._buffer) / self.period
        std = var ** 0.5
        upper = mu + self.k * std
        lower = mu - self.k * std
        self._mid.append(mu)
        self._upper.append(upper)
        self._lower.append(lower)
        return {"upper": upper, "mid": mu, "lower": lower}

    def latest(self) -> dict[str, float]:
        return {
            "upper": self._upper[-1] if self._upper else 0.0,
            "mid": self._mid[-1] if self._mid else 0.0,
            "lower": self._lower[-1] if self._lower else 0.0,
        }


@register_indicator("stochastic")
class Stochastic(Indicator):
    def __init__(self, k_period: int = 14, d_period: int = 3) -> None:
        self.k_period = k_period
        self.d_period = d_period
        self._highs: Deque[float] = deque(maxlen=k_period)
        self._lows: Deque[float] = deque(maxlen=k_period)
        self._k: list[float] = []
        self._d: list[float] = []

    def update(self, candle: dict) -> dict[str, float]:
        self._highs.append(float(candle["high"]))
        self._lows.append(float(candle["low"]))
        c = float(candle["close"])
        if len(self._highs) < self.k_period:
            self._k.append(50.0)
            self._d.append(50.0)
            return {"k": 50.0, "d": 50.0}
        hi = max(self._highs)
        lo = min(self._lows)
        k = 100.0 * (c - lo) / (hi - lo) if hi != lo else 50.0
        self._k.append(k)
        d = sum(self._k[-self.d_period:]) / min(len(self._k), self.d_period)
        self._d.append(d)
        return {"k": k, "d": d}

    def latest(self) -> dict[str, float]:
        return {
            "k": self._k[-1] if self._k else 50.0,
            "d": self._d[-1] if self._d else 50.0,
        }


@register_indicator("adx")
class ADX(Indicator):
    def __init__(self, period: int = 14) -> None:
        self.period = period
        self._tr: Deque[float] = deque(maxlen=period)
        self._plus_dm: Deque[float] = deque(maxlen=period)
        self._minus_dm: Deque[float] = deque(maxlen=period)
        self._prev_high: float | None = None
        self._prev_low: float | None = None
        self._prev_close: float | None = None
        self._values: list[float] = []

    def update(self, candle: dict) -> float:
        h = float(candle["high"])
        l = float(candle["low"])
        c = float(candle["close"])
        if self._prev_high is None:
            self._prev_high, self._prev_low, self._prev_close = h, l, c
            self._values.append(0.0)
            return 0.0
        up_move = h - self._prev_high
        down_move = self._prev_low - l
        plus_dm = up_move if up_move > down_move and up_move > 0 else 0.0
        minus_dm = down_move if down_move > up_move and down_move > 0 else 0.0
        tr = max(h - l, abs(h - self._prev_close), abs(l - self._prev_close))
        self._tr.append(tr)
        self._plus_dm.append(plus_dm)
        self._minus_dm.append(minus_dm)
        self._prev_high, self._prev_low, self._prev_close = h, l, c
        if len(self._tr) < self.period:
            self._values.append(0.0)
            return 0.0
        avg_tr = sum(self._tr) / self.period or 1e-9
        plus_di = 100.0 * sum(self._plus_dm) / self.period / avg_tr
        minus_di = 100.0 * sum(self._minus_dm) / self.period / avg_tr
        dx = 100.0 * abs(plus_di - minus_di) / (plus_di + minus_di + 1e-9)
        self._values.append(dx)
        return dx

    def latest(self) -> float:
        return self._values[-1] if self._values else 0.0
