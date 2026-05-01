"""
Strategy evaluator — turns an AST + context into rule outcomes.

Context:

* ``indicators``: dict[alias -> tuple[float...] | float]  (latest values)
* ``ohlcv``: list of past candles (newest last)
* ``state``: persisted strategy state (positions, last_signal, ...)
* ``parameters``: strategy.parameters merged with backtest-supplied values
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Sequence

from alphaforge_shared.exceptions import StrategyRuntimeError
from alphaforge_worker.dsl.ast import (
    BinOp,
    Bool,
    Expr,
    FunctionCall,
    Number,
    Rule,
    StrategyDoc,
    String,
    Symbol,
    UnaryOp,
)


@dataclass
class EvalContext:
    indicators: dict[str, Any] = field(default_factory=dict)
    indicators_history: dict[str, list[float]] = field(default_factory=dict)
    ohlcv: list[dict] = field(default_factory=list)
    state: dict[str, Any] = field(default_factory=dict)
    parameters: dict[str, Any] = field(default_factory=dict)
    last_close: float = 0.0


@dataclass
class RuleOutcome:
    rule_index: int
    action: str            # buy/sell/close/hold/alert
    size: float | None
    fired: bool
    reasons: list[str] = field(default_factory=list)


class StrategyEvaluator:
    def __init__(self, strategy: StrategyDoc) -> None:
        self.strategy = strategy

    def evaluate(self, ctx: EvalContext) -> list[RuleOutcome]:
        outcomes: list[RuleOutcome] = []
        for i, rule in enumerate(self.strategy.rules):
            try:
                cond_value = self._eval(rule.when, ctx)
            except Exception as exc:  # noqa: BLE001
                raise StrategyRuntimeError(f"rule {i} when() failed: {exc}") from exc
            fired = bool(cond_value)
            size: float | None = None
            if fired and rule.size is not None:
                try:
                    size_value = self._eval(rule.size, ctx)
                    size = float(size_value)
                except Exception as exc:  # noqa: BLE001
                    raise StrategyRuntimeError(f"rule {i} size() failed: {exc}") from exc
            outcomes.append(
                RuleOutcome(
                    rule_index=i,
                    action=rule.then,
                    size=size,
                    fired=fired,
                    reasons=self._explain(rule.when, ctx) if fired else [],
                )
            )
        return outcomes

    # ── core eval ─────────────────────────────────────────────────────────────
    def _eval(self, node: Expr, ctx: EvalContext) -> Any:
        if isinstance(node, Number):
            return node.value
        if isinstance(node, Bool):
            return node.value
        if isinstance(node, String):
            return node.value
        if isinstance(node, Symbol):
            return self._lookup(node.name, ctx)
        if isinstance(node, FunctionCall):
            return self._call(node, ctx)
        if isinstance(node, BinOp):
            return self._binop(node, ctx)
        if isinstance(node, UnaryOp):
            v = self._eval(node.operand, ctx)
            if node.op == "not":
                return not bool(v)
            if node.op == "-":
                return -float(v)
        raise StrategyRuntimeError(f"unsupported node: {node!r}")

    def _lookup(self, name: str, ctx: EvalContext) -> Any:
        if name in ctx.indicators:
            v = ctx.indicators[name]
            if isinstance(v, (list, tuple)) and v:
                return v[-1]
            return v
        if name in ctx.parameters:
            return ctx.parameters[name]
        if name == "close":
            return ctx.last_close
        if name == "ohlcv":
            return ctx.ohlcv
        if name in ctx.state:
            return ctx.state[name]
        if name in {"true", "True", "yes"}:
            return True
        if name in {"false", "False", "no"}:
            return False
        raise StrategyRuntimeError(f"unknown identifier: {name}")

    def _binop(self, node: BinOp, ctx: EvalContext) -> Any:
        l = self._eval(node.left, ctx)
        r = self._eval(node.right, ctx)
        op = node.op
        if op == "and":
            return bool(l) and bool(r)
        if op == "or":
            return bool(l) or bool(r)
        if op in ("+", "-", "*", "/", "%"):
            return _arith(op, l, r)
        if op in ("==", "!="):
            return (l == r) if op == "==" else (l != r)
        if op in (">", "<", ">=", "<="):
            return _cmp(op, l, r)
        raise StrategyRuntimeError(f"unsupported binop {op}")

    # ── functions ─────────────────────────────────────────────────────────────
    def _call(self, node: FunctionCall, ctx: EvalContext) -> Any:
        name = node.name
        args = [self._eval(a, ctx) for a in node.args]
        fn = _FUNCTIONS.get(name)
        if fn is None:
            # series accessors like "fast[-1]" emulated as fn("at", series, idx)
            raise StrategyRuntimeError(f"unknown function: {name}")
        return fn(args, ctx)

    def _explain(self, when: Expr, ctx: EvalContext) -> list[str]:
        notes: list[str] = []
        try:
            for sym in _collect_symbols(when):
                if sym in ctx.indicators:
                    val = ctx.indicators[sym]
                    if isinstance(val, (list, tuple)) and val:
                        val = val[-1]
                    notes.append(f"{sym}={val:.4f}" if isinstance(val, (int, float)) else f"{sym}={val}")
        except Exception:
            pass
        return notes


def _collect_symbols(node: Expr) -> set[str]:
    out: set[str] = set()
    if isinstance(node, Symbol):
        out.add(node.name)
    elif isinstance(node, BinOp):
        out |= _collect_symbols(node.left)
        out |= _collect_symbols(node.right)
    elif isinstance(node, UnaryOp):
        out |= _collect_symbols(node.operand)
    elif isinstance(node, FunctionCall):
        for a in node.args:
            out |= _collect_symbols(a)
    return out


# ── built-in helpers ──────────────────────────────────────────────────────────
def _arith(op: str, l: Any, r: Any) -> Any:
    a, b = float(l), float(r)
    if op == "+":
        return a + b
    if op == "-":
        return a - b
    if op == "*":
        return a * b
    if op == "/":
        if b == 0:
            return 0.0
        return a / b
    if op == "%":
        if b == 0:
            return 0.0
        return a % b
    raise StrategyRuntimeError(op)


def _cmp(op: str, l: Any, r: Any) -> bool:
    a, b = float(l), float(r)
    return {
        ">": a > b,
        "<": a < b,
        ">=": a >= b,
        "<=": a <= b,
    }[op]


def _series(value: Any, ctx: EvalContext, fallback_history_key: str | None = None) -> list[float]:
    if isinstance(value, (list, tuple)):
        return list(value)
    if fallback_history_key and fallback_history_key in ctx.indicators_history:
        return list(ctx.indicators_history[fallback_history_key])
    return [float(value)]


def _fn_cross_up(args: Sequence[Any], ctx: EvalContext) -> bool:
    if len(args) < 2:
        return False
    a, b = args[0], args[1]
    a_series = _series(a, ctx)
    b_series = _series(b, ctx)
    if len(a_series) < 2 or len(b_series) < 2:
        return False
    return a_series[-2] < b_series[-2] and a_series[-1] > b_series[-1]


def _fn_cross_down(args: Sequence[Any], ctx: EvalContext) -> bool:
    if len(args) < 2:
        return False
    a, b = args[0], args[1]
    a_series = _series(a, ctx)
    b_series = _series(b, ctx)
    if len(a_series) < 2 or len(b_series) < 2:
        return False
    return a_series[-2] > b_series[-2] and a_series[-1] < b_series[-1]


def _fn_above(args: Sequence[Any], ctx: EvalContext) -> bool:
    return float(args[0]) > float(args[1])


def _fn_below(args: Sequence[Any], ctx: EvalContext) -> bool:
    return float(args[0]) < float(args[1])


def _fn_min(args: Sequence[Any], ctx: EvalContext) -> float:
    flat = [float(v) for v in _flatten(args)]
    return min(flat) if flat else 0.0


def _fn_max(args: Sequence[Any], ctx: EvalContext) -> float:
    flat = [float(v) for v in _flatten(args)]
    return max(flat) if flat else 0.0


def _fn_abs(args: Sequence[Any], ctx: EvalContext) -> float:
    return abs(float(args[0])) if args else 0.0


def _fn_pct_change(args: Sequence[Any], ctx: EvalContext) -> float:
    series = _series(args[0], ctx)
    if len(series) < 2 or series[0] == 0:
        return 0.0
    return (series[-1] - series[0]) / series[0]


def _fn_in_range(args: Sequence[Any], ctx: EvalContext) -> bool:
    return float(args[1]) <= float(args[0]) <= float(args[2])


def _fn_position(args: Sequence[Any], ctx: EvalContext) -> float:
    return float(ctx.state.get("position", 0))


def _fn_param(args: Sequence[Any], ctx: EvalContext) -> Any:
    name = args[0] if isinstance(args[0], str) else str(args[0])
    return ctx.parameters.get(name)


def _flatten(values: Iterable[Any]) -> Iterable[Any]:
    for v in values:
        if isinstance(v, (list, tuple)):
            yield from _flatten(v)
        else:
            yield v


_FUNCTIONS = {
    "cross_up": _fn_cross_up,
    "cross_down": _fn_cross_down,
    "above": _fn_above,
    "below": _fn_below,
    "min": _fn_min,
    "max": _fn_max,
    "abs": _fn_abs,
    "pct_change": _fn_pct_change,
    "in_range": _fn_in_range,
    "position": _fn_position,
    "param": _fn_param,
}
