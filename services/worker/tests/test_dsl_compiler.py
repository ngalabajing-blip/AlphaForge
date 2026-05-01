import pytest

from alphaforge_shared.exceptions import StrategyParseError
from alphaforge_worker.dsl.ast import BinOp, FunctionCall, Number, Symbol, UnaryOp
from alphaforge_worker.dsl.compiler import compile_expression


def test_number():
    assert compile_expression("42") == Number(42)


def test_simple_call():
    e = compile_expression("cross_up(fast, slow)")
    assert isinstance(e, FunctionCall)
    assert e.name == "cross_up"
    assert e.args[0] == Symbol("fast")
    assert e.args[1] == Symbol("slow")


def test_binop():
    e = compile_expression("fast > slow + 5")
    assert isinstance(e, BinOp) and e.op == ">"
    assert isinstance(e.right, BinOp) and e.right.op == "+"


def test_logical():
    e = compile_expression("rsi < 30 and volume > 1000")
    assert isinstance(e, BinOp) and e.op == "and"


def test_negation():
    e = compile_expression("not bull")
    assert isinstance(e, UnaryOp) and e.op == "not"


def test_invalid():
    with pytest.raises(StrategyParseError):
        compile_expression("((((")


def test_trailing():
    with pytest.raises(StrategyParseError):
        compile_expression("1 + 1 garbage")
