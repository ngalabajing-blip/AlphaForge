from __future__ import annotations

import math

from alphaforge_ml.features import build_window_features


def _trades(n: int, side_bias: float = 0.5) -> list[dict]:
    return [
        {
            "symbol": "ETH/USDT",
            "side": "buy" if (i % 100) / 100 < side_bias else "sell",
            "amount": 1.0 + i * 0.01,
            "price": 100.0 + (i % 7),
            "ts": float(i),
        }
        for i in range(n)
    ]


def test_features_zero_trades_safe() -> None:
    feats = build_window_features([], [], [])
    assert feats["trade_count"] == 0
    assert feats["buy_sell_ratio"] == 0
    assert feats["volatility"] == 0


def test_features_normal_volume() -> None:
    feats = build_window_features(_trades(200), [], [])
    assert feats["trade_count"] == 200
    assert 0 <= feats["buy_sell_ratio"] <= 1


def test_features_volatility_increases_with_noise() -> None:
    quiet = [{"price": 100.0, "ts": float(i), "side": "buy", "amount": 1.0, "symbol": "x"} for i in range(50)]
    loud = [
        {"price": 100.0 + math.sin(i / 3) * 10.0, "ts": float(i), "side": "buy", "amount": 1.0, "symbol": "x"}
        for i in range(50)
    ]
    quiet_feats = build_window_features(quiet, [], [])
    loud_feats = build_window_features(loud, [], [])
    assert loud_feats["volatility"] >= quiet_feats["volatility"]
