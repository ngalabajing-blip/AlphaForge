from __future__ import annotations

import math

from alphaforge_quantcore import OrderBook, atr, ema, rsi, vwap


def test_orderbook_match_partial() -> None:
    book = OrderBook()
    book.submit(1, "sell", 100.0, 5.0)
    book.submit(2, "sell", 100.5, 5.0)
    trades = book.submit(3, "buy", 100.5, 8.0)
    total = sum(t.quantity for t in trades)
    assert math.isclose(total, 8.0, abs_tol=1e-9)


def test_ema_returns_correct_length() -> None:
    values = [float(i) for i in range(100)]
    out = ema(values, period=14)
    assert len(out) == len(values)
    assert out[-1] > out[10]


def test_rsi_bounds() -> None:
    values = [50 + 10 * math.sin(i / 5) for i in range(100)]
    out = rsi(values, period=14)
    for x in out:
        assert math.isnan(x) or 0.0 <= x <= 100.0


def test_atr_non_negative() -> None:
    highs = [100 + i * 0.5 for i in range(80)]
    lows = [h - 1.0 for h in highs]
    closes = [h - 0.5 for h in highs]
    out = atr(highs, lows, closes, period=14)
    assert all(math.isnan(x) or x >= 0 for x in out)


def test_vwap_constant_price() -> None:
    prices = [100.0] * 30
    volumes = [1.0] * 30
    out = vwap(prices, volumes)
    assert all(math.isclose(x, 100.0, abs_tol=1e-9) for x in out)
