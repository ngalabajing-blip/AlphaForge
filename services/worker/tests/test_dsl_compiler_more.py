from __future__ import annotations

import pytest
from alphaforge_shared.exceptions import StrategyParseError
from alphaforge_worker.dsl.parser import parse_strategy

VALID = """\
strategy: "x"
universe: { symbols: [ETH/USDT], timeframe: 1h }
indicators:
  - {name: ema, alias: fast, period: 12}
  - {name: ema, alias: slow, period: 26}
rules:
  - when: cross_up(fast, slow)
    then: buy
    size: 0.2
"""


def test_parses_valid_program() -> None:
    doc = parse_strategy(VALID)
    assert doc.name == "x"
    aliases = [ind.alias for ind in doc.indicators]
    assert "fast" in aliases and "slow" in aliases
    assert len(doc.rules) == 1
    assert doc.rules[0].then == "buy"


def test_missing_strategy_key_raises() -> None:
    bad = "universe: { symbols: [ETH/USDT], timeframe: 1h }\nrules: []\n"
    with pytest.raises(StrategyParseError):
        parse_strategy(bad)


def test_empty_document_raises() -> None:
    with pytest.raises(StrategyParseError):
        parse_strategy("")


def test_dict_input_works() -> None:
    doc = parse_strategy(
        {
            "strategy": "from-dict",
            "universe": {"symbols": ["BTC/USDT"], "timeframe": "1h"},
            "indicators": [{"name": "rsi", "alias": "r", "period": 14}],
            "rules": [{"when": "r < 30", "then": "buy"}],
        }
    )
    assert doc.name == "from-dict"
    assert doc.indicators[0].alias == "r"


def test_buy_without_size_defaults() -> None:
    src = VALID.replace("    size: 0.2\n", "")
    doc = parse_strategy(src)
    assert doc.rules[0].size is None
