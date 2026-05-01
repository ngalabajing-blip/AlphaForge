import pytest
from alphaforge_shared.exceptions import StrategyParseError
from alphaforge_worker.dsl.parser import parse_strategy

YAML = """
strategy: ema-cross
universe:
  symbols: [ETH/USDC, BTC/USDC]
  timeframe: 1h
indicators:
  - {name: ema, period: 12, alias: fast}
  - {name: ema, period: 26, alias: slow}
  - {name: rsi, period: 14, alias: rsi14}
rules:
  - when: cross_up(fast, slow)
    then: buy
    size: 0.2
  - when: cross_down(fast, slow)
    then: close
risk:
  per_trade: 0.02
  max_drawdown: 0.4
  max_position_pct: 0.6
parameters:
  cooldown: 600
"""


def test_parse_full():
    doc = parse_strategy(YAML)
    assert doc.name == "ema-cross"
    assert "ETH/USDC" in doc.universe.symbols
    assert len(doc.indicators) == 3
    assert doc.indicators[0].alias == "fast"
    assert len(doc.rules) == 2
    assert doc.rules[0].then == "buy"
    assert doc.risk.max_position_pct == 0.6
    assert doc.parameters["cooldown"] == 600


def test_missing_rules():
    with pytest.raises(StrategyParseError):
        parse_strategy("""
strategy: x
universe: {symbols: [A], timeframe: 1h}
""")


def test_invalid_then():
    with pytest.raises(StrategyParseError):
        parse_strategy("""
strategy: x
universe: {symbols: [A], timeframe: 1h}
rules:
  - when: 1 == 1
    then: hodl
""")
