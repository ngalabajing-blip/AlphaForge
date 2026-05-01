from datetime import datetime, timezone

from alphaforge_ml.features.extractors import (
    extract_candle_features,
    extract_trade_window,
)


def test_trade_window_empty():
    f = extract_trade_window([])
    assert f.n_trades == 0
    assert f.buy_ratio == 0.5


def test_trade_window_fields():
    trades = [
        {"amount_in": 1, "side": "buy", "buyer": "a", "price": 100, "ts": datetime.now(tz=timezone.utc)},
        {"amount_in": 2, "side": "sell", "buyer": "b", "price": 110, "ts": datetime.now(tz=timezone.utc)},
        {"amount_in": 3, "side": "buy", "buyer": "a", "price": 105, "ts": datetime.now(tz=timezone.utc)},
    ]
    f = extract_trade_window(trades)
    assert f.n_trades == 3
    assert f.unique_addresses == 2
    assert f.total_volume == 6.0
    assert 0 <= f.buy_ratio <= 1


def test_candle_features_basic():
    candles = []
    for i in range(50):
        candles.append({
            "ts": datetime.now(tz=timezone.utc),
            "open": 100 + i, "high": 101 + i, "low": 99 + i, "close": 100 + i,
            "volume": 5,
        })
    rows = extract_candle_features(candles, fast=5, slow=10)
    assert len(rows) == 50
    assert rows[-1].sma_slow > 0
    assert 0 <= rows[-1].rsi <= 100
