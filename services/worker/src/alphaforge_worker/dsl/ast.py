"""AST types for the AlphaForge Strategy DSL.

A parsed strategy looks like::

    StrategyDoc(
        name="ema-cross",
        universe=Universe(symbols=["ETH/USDC"], timeframe="1h"),
        indicators=[Indicator(name="ema", alias="fast", params={"period": 12}), ...],
        rules=[Rule(when=Expr(...), then="buy", size=Expr(...))],
        risk=RiskConfig(per_trade=0.02, max_drawdown=0.4),
    )
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence


# ── expression nodes (compiled lazily by ``compile_expression``) ──────────────
@dataclass(frozen=True)
class Number:
    value: float


@dataclass(frozen=True)
class Bool:
    value: bool


@dataclass(frozen=True)
class String:
    value: str


@dataclass(frozen=True)
class Symbol:
    name: str


@dataclass(frozen=True)
class FunctionCall:
    name: str
    args: tuple["Expr", ...] = ()


@dataclass(frozen=True)
class BinOp:
    op: str
    left: "Expr"
    right: "Expr"


@dataclass(frozen=True)
class UnaryOp:
    op: str
    operand: "Expr"


Expr = Number | Bool | String | Symbol | FunctionCall | BinOp | UnaryOp


# ── document-level nodes ──────────────────────────────────────────────────────
@dataclass(frozen=True)
class Indicator:
    name: str
    alias: str
    params: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Rule:
    when: Expr
    then: str         # buy, sell, close, hold, alert
    size: Expr | None = None
    note: str | None = None


@dataclass(frozen=True)
class Universe:
    symbols: tuple[str, ...]
    timeframe: str


@dataclass(frozen=True)
class RiskConfig:
    per_trade: float = 0.02
    max_drawdown: float = 0.5
    max_position_pct: float = 0.5
    stop_loss_pct: float | None = None
    take_profit_pct: float | None = None
    daily_loss_limit_pct: float | None = None


@dataclass(frozen=True)
class StrategyDoc:
    name: str
    universe: Universe
    indicators: tuple[Indicator, ...]
    rules: tuple[Rule, ...]
    risk: RiskConfig
    parameters: dict[str, Any] = field(default_factory=dict)
    description: str | None = None
