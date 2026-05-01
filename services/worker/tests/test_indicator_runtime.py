from __future__ import annotations

import math

# Importing the package __init__ triggers indicator registration via @register_indicator
import alphaforge_worker.indicators  # noqa: F401
from alphaforge_worker.indicators.registry import INDICATORS


def _candle(close: float, ts: int = 0) -> dict:
    return {
        "ts": ts,
        "open": close,
        "high": close * 1.001,
        "low": close * 0.999,
        "close": close,
        "volume": 100.0,
    }


def test_registry_has_core_indicators() -> None:
    for name in ("ema", "sma", "rsi", "macd", "atr", "bollinger"):
        assert name in INDICATORS, f"{name} should be registered"


def test_ema_streams_close() -> None:
    cls = INDICATORS["ema"]
    inst = cls(period=5)
    closes = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]
    out: list[float] = []
    for i, c in enumerate(closes):
        v = inst.update(_candle(c, ts=i))
        out.append(float(v) if v is not None else float("nan"))
    last = inst.latest()
    assert last is not None
    assert 1.0 <= float(last) <= 7.0


def test_rsi_bounded() -> None:
    cls = INDICATORS["rsi"]
    inst = cls(period=14)
    for i in range(60):
        c = 50 + math.sin(i / 4) * 5
        inst.update(_candle(c, ts=i))
    v = inst.latest()
    assert v is None or 0.0 <= float(v) <= 100.0


def test_unknown_indicator_missing() -> None:
    assert "totally_not_real" not in INDICATORS
