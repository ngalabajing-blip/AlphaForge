from __future__ import annotations

from alphaforge_worker.dsl.evaluator import EvalContext, StrategyEvaluator
from alphaforge_worker.dsl.parser import parse_strategy


def _eval_expr(src: str, ctx: EvalContext) -> object:
    """Helper: build a 1-rule strategy whose `when` is the given expression."""
    doc = parse_strategy(
        {
            "strategy": "x",
            "universe": {"symbols": ["ETH/USDT"], "timeframe": "1h"},
            "rules": [{"when": src, "then": "buy"}],
        }
    )
    return StrategyEvaluator(doc).evaluate(ctx)[0].fired


def test_basic_arithmetic_via_rule() -> None:
    ctx = EvalContext(parameters={"x": 5})
    out = _eval_expr("x + 3 > 7", ctx)
    assert out is True


def test_logical_and() -> None:
    ctx = EvalContext(parameters={"a": 1, "b": 0})
    assert _eval_expr("a and b", ctx) is False
    assert _eval_expr("a or b", ctx) is True


def test_comparison_returns_bool() -> None:
    ctx = EvalContext(parameters={"a": 10, "b": 5})
    assert _eval_expr("a > b", ctx) is True
    assert _eval_expr("a < b", ctx) is False


def test_cross_up_function() -> None:
    # last bar: fast crosses above slow (fast was below, now above)
    ctx = EvalContext(
        indicators={"fast": 5, "slow": 4},
        indicators_history={"fast": [1, 2, 3, 5], "slow": [3, 3, 4, 4]},
    )
    assert _eval_expr("cross_up(fast, slow)", ctx) is True


def test_unary_negation() -> None:
    ctx = EvalContext(parameters={"a": 3})
    assert _eval_expr("-a < 0", ctx) is True


def test_unknown_identifier_raises_runtime_error() -> None:
    import pytest
    from alphaforge_shared.exceptions import StrategyRuntimeError

    ctx = EvalContext()
    with pytest.raises(StrategyRuntimeError):
        _eval_expr("totally_undefined > 1", ctx)
