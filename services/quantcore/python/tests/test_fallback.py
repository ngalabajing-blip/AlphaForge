"""Verify the Python fallback implementations (used when Rust extension unavailable)."""
from alphaforge_quantcore import OrderBook, ema, rsi, atr, vwap


def test_book_match():
    book = OrderBook()
    book.submit("sell", 101.0, 5.0)
    trades = book.submit("buy", 102.0, 5.0)
    assert len(trades) == 1
    assert trades[0].price == 101.0
    assert trades[0].quantity == 5.0


def test_book_partial_fill():
    book = OrderBook()
    book.submit("sell", 100.0, 2.0)
    trades = book.submit("buy", 100.0, 5.0)
    assert sum(t.quantity for t in trades) == 2.0
    assert book.best_bid() == 100.0


def test_ema_constant():
    out = ema([5.0] * 30, 10)
    assert all(abs(v - 5.0) < 1e-9 for v in out)


def test_rsi_bounds():
    out = rsi([float(i) for i in range(50)], 14)
    assert all(0 <= v <= 100 for v in out)


def test_atr_positive():
    h = [10.0 + i for i in range(20)]
    l = [9.0 + i for i in range(20)]
    c = [9.5 + i for i in range(20)]
    out = atr(h, l, c, 14)
    assert all(v >= 0 for v in out)


def test_vwap_grows_with_higher_prices():
    p = [10.0, 20.0, 30.0]
    v = [1.0, 1.0, 1.0]
    w = vwap(p, v)
    assert w[0] == 10.0 < w[1] < w[2]
