from __future__ import annotations

import math
from datetime import UTC, datetime, timedelta

from alphaforge_ml.features.extractors import (
    TradeWindowFeatures,
    extract_candle_features,
    extract_trade_window,
)


def _trades(n: int, *, side_bias: float = 0.5) -> list[dict]:
    base = datetime(2024, 1, 1, tzinfo=UTC)
    return [
        {
            "buyer": f"0xaddr{i % 7}",
            "side": "buy" if (i % 100) / 100 < side_bias else "sell",
            "amount_in": 1.0 + (i % 5),
            "amount_out": 100.0 + (i % 7),
            "ts": base + timedelta(seconds=i),
        }
        for i in range(n)
    ]


def _candles(n: int) -> list[dict]:
    out: list[dict] = []
    base = datetime(2024, 1, 1, tzinfo=UTC)
    p = 100.0
    for i in range(n):
        p += math.sin(i / 5) * 0.5
        out.append(
            {
                "ts": base + timedelta(minutes=i),
                "open": p,
                "high": p * 1.005,
                "low": p * 0.995,
                "close": p + 0.1,
                "volume": 10.0 + i,
            }
        )
    return out


def test_extract_trade_window_handles_empty() -> None:
    feats = extract_trade_window([])
    assert isinstance(feats, TradeWindowFeatures)
    assert feats.n_trades == 0
    assert feats.total_volume == 0
    assert 0 <= feats.buy_ratio <= 1


def test_extract_trade_window_basic_stats() -> None:
    feats = extract_trade_window(_trades(50, side_bias=0.8))
    assert feats.n_trades == 50
    assert feats.total_volume > 0
    assert 0.6 < feats.buy_ratio <= 1.0
    assert feats.unique_addresses > 0
    vec = feats.as_vector()
    assert len(vec) == 8
    assert all(isinstance(v, float) for v in vec)


def test_extract_candle_features_returns_rows() -> None:
    rows = extract_candle_features(_candles(40))
    assert len(rows) == 40
    # last row should have a finite close (`c` attr in CandleFeatureRow)
    assert math.isfinite(rows[-1].c)
    assert math.isfinite(rows[-1].rsi)
