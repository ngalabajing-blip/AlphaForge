from __future__ import annotations

import pytest

from alphaforge_worker.dsl.parser import parse_strategy
from alphaforge_worker.dsl.compiler import compile_strategy
from alphaforge_worker.dsl.errors import DSLError


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


def test_compiles_valid_program() -> None:
    program = parse_strategy(VALID)
    plan = compile_strategy(program)
    assert plan.name == "x"
    assert "fast" in plan.indicator_names
    assert "slow" in plan.indicator_names
    assert plan.rules
    assert plan.rules[0].action == "buy"


def test_invalid_indicator_raises() -> None:
    bad = VALID.replace("name: ema", "name: __not_a_real_indicator__", 1)
    with pytest.raises(DSLError):
        compile_strategy(parse_strategy(bad))


def test_unknown_alias_in_rule() -> None:
    bad = VALID.replace("cross_up(fast, slow)", "cross_up(fast, MISSING)")
    with pytest.raises(DSLError):
        compile_strategy(parse_strategy(bad))


def test_buy_without_size_defaults() -> None:
    src = VALID.replace("size: 0.2\n", "")
    plan = compile_strategy(parse_strategy(src))
    assert plan.rules[0].size_expr is None
