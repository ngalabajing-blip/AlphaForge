from __future__ import annotations

import pytest
from alphaforge_api.services.dsl_loader import loads

VALID_YAML = """\
strategy: "test"
universe: { symbols: [ETH/USDT], timeframe: 1h }
indicators:
  - {name: ema, alias: fast, period: 12}
  - {name: ema, alias: slow, period: 26}
rules:
  - when: cross_up(fast, slow)
    then: buy
"""


def test_loads_valid_strategy() -> None:
    parsed = loads(VALID_YAML)
    assert parsed["strategy"] == "test"
    assert len(parsed["indicators"]) == 2
    assert parsed["rules"][0]["then"] == "buy"
    # _normalise should add defaults
    assert "parameters" in parsed
    assert "risk" in parsed


def test_loads_json_format() -> None:
    parsed = loads("""{"strategy":"j","universe":{"symbols":["ETH/USDT"],"timeframe":"1h"},
            "rules":[{"when":"cross_up(a,b)","then":"buy"}]}""")
    assert parsed["strategy"] == "j"
    assert parsed["rules"][0]["then"] == "buy"


def test_empty_raises() -> None:
    with pytest.raises(ValueError):
        loads("")


def test_missing_rules_raises() -> None:
    with pytest.raises(ValueError):
        loads("strategy: x\nuniverse: { symbols: [ETH/USDT], timeframe: 1h }\nrules: []\n")


def test_missing_required_field() -> None:
    with pytest.raises(ValueError):
        loads("indicators: []\nrules:\n  - {when: a, then: buy}\n")


def test_invalid_top_level_scalar() -> None:
    with pytest.raises(ValueError):
        loads('"just a string"')
