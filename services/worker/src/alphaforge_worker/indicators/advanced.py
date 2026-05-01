"""Volume / volatility / channel indicators."""
from __future__ import annotations

from collections import deque
from typing import Any, Deque

from alphaforge_worker.indicators.basic import ATR, EMA, SMA
from alphaforge_worker.indicators.registry import Indicator, register_indicator


@register_indicator("obv")
class OBV(Indicator):
    def __init__(self) -> None:
        self._values: list[float] = []
        self._prev_close: float | None = None

    def update(self, candle: dict) -> float:
        c = float(candle["close"])
        v = float(candle.get("volume", 0))
        prev = self._values[-1] if self._values else 0.0
        if self._prev_close is None or c == self._prev_close:
            self._values.append(prev)
        elif c > self._prev_close:
            self._values.append(prev + v)
        else:
            self._values.append(prev - v)
        self._prev_close = c
        return self._values[-1]

    def latest(self) -> float:
        return self._values[-1] if self._values else 0.0


@register_indicator("vwap")
class VWAP(Indicator):
    def __init__(self) -> None:
        self._cum_pv: float = 0.0
        self._cum_v: float = 0.0
        self._values: list[float] = []

    def update(self, candle: dict) -> float:
        typical = (float(candle["high"]) + float(candle["low"]) + float(candle["close"])) / 3.0
        v = float(candle.get("volume", 0))
        self._cum_pv += typical * v
        self._cum_v += v
        vwap = self._cum_pv / self._cum_v if self._cum_v else typical
        self._values.append(vwap)
        return vwap

    def latest(self) -> float:
        return self._values[-1] if self._values else 0.0


@register_indicator("aroon")
class Aroon(Indicator):
    def __init__(self, period: int = 25) -> None:
        self.period = period
        self._highs: Deque[float] = deque(maxlen=period)
        self._lows: Deque[float] = deque(maxlen=period)
        self._up: list[float] = []
        self._down: list[float] = []

    def update(self, candle: dict) -> dict[str, float]:
        self._highs.append(float(candle["high"]))
        self._lows.append(float(candle["low"]))
        if len(self._highs) < self.period:
            self._up.append(50.0)
            self._down.append(50.0)
            return {"up": 50.0, "down": 50.0}
        # idx_max: index of max high in window (0 = oldest, period-1 = newest)
        max_h = max(self._highs)
        min_l = min(self._lows)
        idx_high = list(self._highs).index(max_h)
        idx_low = list(self._lows).index(min_l)
        up = 100.0 * (idx_high) / (self.period - 1)
        down = 100.0 * (idx_low) / (self.period - 1)
        self._up.append(up)
        self._down.append(down)
        return {"up": up, "down": down}

    def latest(self) -> dict[str, float]:
        return {
            "up": self._up[-1] if self._up else 50.0,
            "down": self._down[-1] if self._down else 50.0,
        }


@register_indicator("cmf")
class ChaikinMoneyFlow(Indicator):
    def __init__(self, period: int = 20) -> None:
        self.period = period
        self._mfv: Deque[float] = deque(maxlen=period)
        self._volumes: Deque[float] = deque(maxlen=period)
        self._values: list[float] = []

    def update(self, candle: dict) -> float:
        h, l, c = float(candle["high"]), float(candle["low"]), float(candle["close"])
        v = float(candle.get("volume", 0))
        if h == l:
            mfv = 0.0
        else:
            mfm = ((c - l) - (h - c)) / (h - l)
            mfv = mfm * v
        self._mfv.append(mfv)
        self._volumes.append(v)
        cmf = sum(self._mfv) / sum(self._volumes) if sum(self._volumes) else 0.0
        self._values.append(cmf)
        return cmf

    def latest(self) -> float:
        return self._values[-1] if self._values else 0.0


@register_indicator("donchian")
class Donchian(Indicator):
    def __init__(self, period: int = 20) -> None:
        self.period = period
        self._highs: Deque[float] = deque(maxlen=period)
        self._lows: Deque[float] = deque(maxlen=period)

    def update(self, candle: dict) -> dict[str, float]:
        self._highs.append(float(candle["high"]))
        self._lows.append(float(candle["low"]))
        return {
            "upper": max(self._highs),
            "lower": min(self._lows),
            "mid": (max(self._highs) + min(self._lows)) / 2,
        }

    def latest(self) -> dict[str, float]:
        if not self._highs:
            return {"upper": 0.0, "lower": 0.0, "mid": 0.0}
        return {
            "upper": max(self._highs),
            "lower": min(self._lows),
            "mid": (max(self._highs) + min(self._lows)) / 2,
        }


@register_indicator("ichimoku")
class Ichimoku(Indicator):
    def __init__(self, conversion: int = 9, base: int = 26, span_b: int = 52) -> None:
        self.cd = conversion
        self.bd = base
        self.sd = span_b
        self._highs: Deque[float] = deque(maxlen=max(conversion, base, span_b))
        self._lows: Deque[float] = deque(maxlen=max(conversion, base, span_b))

    def _midband(self, period: int) -> float:
        if not self._highs or len(self._highs) < period:
            return 0.0
        highs = list(self._highs)[-period:]
        lows = list(self._lows)[-period:]
        return (max(highs) + min(lows)) / 2

    def update(self, candle: dict) -> dict[str, float]:
        self._highs.append(float(candle["high"]))
        self._lows.append(float(candle["low"]))
        return {
            "conversion": self._midband(self.cd),
            "base": self._midband(self.bd),
            "span_a": (self._midband(self.cd) + self._midband(self.bd)) / 2,
            "span_b": self._midband(self.sd),
        }

    def latest(self) -> dict[str, float]:
        return {
            "conversion": self._midband(self.cd),
            "base": self._midband(self.bd),
            "span_a": (self._midband(self.cd) + self._midband(self.bd)) / 2,
            "span_b": self._midband(self.sd),
        }


@register_indicator("keltner")
class KeltnerChannels(Indicator):
    def __init__(self, ema_period: int = 20, atr_period: int = 10, k: float = 2.0) -> None:
        self.k = k
        self.ema = EMA(ema_period)
        self.atr = ATR(atr_period)
        self._upper: list[float] = []
        self._lower: list[float] = []
        self._mid: list[float] = []

    def update(self, candle: dict) -> dict[str, float]:
        mid = self.ema.update(candle)
        a = self.atr.update(candle)
        upper = mid + self.k * a
        lower = mid - self.k * a
        self._upper.append(upper)
        self._lower.append(lower)
        self._mid.append(mid)
        return {"upper": upper, "lower": lower, "mid": mid}

    def latest(self) -> dict[str, float]:
        return {
            "upper": self._upper[-1] if self._upper else 0.0,
            "lower": self._lower[-1] if self._lower else 0.0,
            "mid": self._mid[-1] if self._mid else 0.0,
        }


@register_indicator("supertrend")
class Supertrend(Indicator):
    def __init__(self, atr_period: int = 10, multiplier: float = 3.0) -> None:
        self.atr = ATR(atr_period)
        self.mult = multiplier
        self._final_upper: float = 0.0
        self._final_lower: float = 0.0
        self._direction: int = 1   # 1 long, -1 short
        self._values: list[float] = []
        self._prev_close: float | None = None

    def update(self, candle: dict) -> float:
        h, l, c = float(candle["high"]), float(candle["low"]), float(candle["close"])
        atr = self.atr.update(candle)
        median = (h + l) / 2
        upper = median + self.mult * atr
        lower = median - self.mult * atr

        if self._prev_close is None:
            self._final_upper = upper
            self._final_lower = lower
            self._direction = 1 if c >= lower else -1
        else:
            self._final_upper = upper if upper < self._final_upper or self._prev_close > self._final_upper else self._final_upper
            self._final_lower = lower if lower > self._final_lower or self._prev_close < self._final_lower else self._final_lower
            if c > self._final_upper:
                self._direction = 1
            elif c < self._final_lower:
                self._direction = -1
        line = self._final_lower if self._direction > 0 else self._final_upper
        self._prev_close = c
        self._values.append(line)
        return line

    def latest(self) -> float:
        return self._values[-1] if self._values else 0.0
