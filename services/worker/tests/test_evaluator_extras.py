from __future__ import annotations

import math

from alphaforge_worker.dsl.evaluator import EvalContext, evaluate_expression
from alphaforge_worker.dsl.parser import parse_expression


def test_basic_arithmetic() -> None:
    ctx = EvalContext(values={}, params={})
    assert evaluate_expression(parse_expression("1 + 2"), ctx) == 3


def test_logical_and_short_circuit() -> None:
    ctx = EvalContext(values={"a": 0, "b": 1}, params={})
    assert evaluate_expression(parse_expression("a and b"), ctx) in (0, False)


def test_comparison_returns_bool() -> None:
    ctx = EvalContext(values={"a": 10, "b": 5}, params={})
    assert evaluate_expression(parse_expression("a > b"), ctx)
    assert not evaluate_expression(parse_expression("a < b"), ctx)


def test_param_substitution() -> None:
    ctx = EvalContext(values={}, params={"x": 7})
    assert evaluate_expression(parse_expression("param(\"x\") * 2"), ctx) == 14


def test_cross_up_function() -> None:
    ctx = EvalContext(
        values={"fast": [1, 2, 3, 5], "slow": [3, 3, 3, 4]},
        params={},
    )
    out = evaluate_expression(parse_expression("cross_up(fast, slow)"), ctx)
    assert bool(out)


def test_unary_negation() -> None:
    ctx = EvalContext(values={}, params={})
    assert evaluate_expression(parse_expression("-5"), ctx) == -5


def test_division_by_zero_safe() -> None:
    ctx = EvalContext(values={}, params={})
    out = evaluate_expression(parse_expression("1 / 0"), ctx)
    assert math.isnan(out) or math.isinf(out)
