from __future__ import annotations

import math

from alphaforge_worker.indicators.registry import build_indicator


def test_ema_registry_contract() -> None:
    inst = build_indicator("ema", {"period": 5})
    closes = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]
    out = inst.compute({"close": closes})
    assert isinstance(out, list)
    assert len(out) == len(closes)


def test_rsi_bounded() -> None:
    inst = build_indicator("rsi", {"period": 14})
    closes = [50 + math.sin(i / 4) * 5 for i in range(60)]
    out = inst.compute({"close": closes})
    for v in out:
        if not math.isnan(v):
            assert 0.0 <= v <= 100.0


def test_unknown_indicator_raises() -> None:
    import pytest
    with pytest.raises(KeyError):
        build_indicator("totally_not_real", {})
