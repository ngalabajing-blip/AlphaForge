import pytest

from alphaforge_api.services.dsl_loader import loads


VALID = """
strategy: ema-cross
universe:
  - ETH/USDC
  - BTC/USDC
indicators:
  - {name: ema, period: 12, alias: fast}
  - {name: ema, period: 26, alias: slow}
rules:
  - when: cross_up(fast, slow)
    then: buy
  - when: cross_down(fast, slow)
    then: close
risk:
  per_trade: 0.02
"""


def test_valid_yaml():
    parsed = loads(VALID)
    assert parsed["strategy"] == "ema-cross"
    assert "universe" in parsed
    assert isinstance(parsed["rules"], list)


def test_missing_required_keys():
    with pytest.raises(ValueError):
        loads("strategy: x\n")


def test_empty():
    with pytest.raises(ValueError):
        loads("")


def test_rules_must_be_nonempty_list():
    bad = """
strategy: x
universe: [ETH/USDC]
rules: {}
"""
    with pytest.raises(ValueError):
        loads(bad)
