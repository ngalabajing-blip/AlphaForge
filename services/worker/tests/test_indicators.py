import math

from alphaforge_worker.indicators import INDICATORS, EMA, RSI, MACD, Bollinger, ATR


def _candles(n=80, base=100):
    return [
        {"open": base + i, "high": base + i + 0.5, "low": base + i - 0.5, "close": base + i, "volume": 10}
        for i in range(n)
    ]


def test_registry_populated():
    assert "sma" in INDICATORS
    assert "ema" in INDICATORS
    assert "rsi" in INDICATORS
    assert len(INDICATORS) >= 14


def test_ema_basic():
    e = EMA(period=10)
    for c in _candles():
        e.update(c)
    assert e.latest() > 0


def test_rsi_bounded():
    r = RSI(period=14)
    for c in _candles():
        r.update(c)
    v = r.latest()
    assert 0 <= v <= 100


def test_macd_returns_dict():
    m = MACD()
    for c in _candles():
        m.update(c)
    last = m.latest()
    assert "macd" in last and "signal" in last and "hist" in last


def test_bollinger_bands_ordered():
    b = Bollinger(period=10)
    for c in _candles():
        b.update(c)
    last = b.latest()
    assert last["lower"] <= last["mid"] <= last["upper"]


def test_atr_positive():
    a = ATR(period=14)
    for c in _candles():
        a.update(c)
    assert a.latest() >= 0
