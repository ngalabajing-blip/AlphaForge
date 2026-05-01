"""
YAML / JSON parser for AlphaForge strategies.

Translates raw documents into the typed :mod:`ast` representation. Expression
strings (``cross_up(fast, slow)``) are compiled by
:mod:`alphaforge_worker.dsl.compiler`.
"""
from __future__ import annotations

from typing import Any, Mapping

import orjson

from alphaforge_shared.exceptions import StrategyParseError
from alphaforge_worker.dsl.ast import (
    Indicator,
    RiskConfig,
    Rule,
    StrategyDoc,
    Universe,
)
from alphaforge_worker.dsl.compiler import compile_expression


def parse_strategy(text: str | dict) -> StrategyDoc:
    if isinstance(text, dict):
        data = text
    else:
        data = _load_text(text)
    return _build(data)


def _load_text(text: str) -> dict[str, Any]:
    text = text.strip()
    if not text:
        raise StrategyParseError("empty document")
    try:
        import yaml  # type: ignore[import-not-found]
    except ImportError:
        yaml = None  # type: ignore[assignment]
    if yaml is not None:
        try:
            data = yaml.safe_load(text)
            if isinstance(data, dict):
                return data
        except yaml.YAMLError:  # type: ignore[attr-defined]
            pass
    try:
        data = orjson.loads(text)
    except Exception as exc:  # noqa: BLE001
        raise StrategyParseError(f"invalid document: {exc}") from exc
    if not isinstance(data, dict):
        raise StrategyParseError("document must be a mapping")
    return data


def _build(data: Mapping[str, Any]) -> StrategyDoc:
    if "strategy" not in data:
        raise StrategyParseError("missing 'strategy' key")
    if "universe" not in data:
        raise StrategyParseError("missing 'universe' key")
    if "rules" not in data or not isinstance(data["rules"], list) or not data["rules"]:
        raise StrategyParseError("'rules' must be a non-empty list")

    name = str(data["strategy"]).strip()

    universe_raw = data["universe"]
    if isinstance(universe_raw, list):
        symbols = tuple(s.strip() for s in universe_raw)
        timeframe = "1h"
    elif isinstance(universe_raw, Mapping):
        symbols = tuple(str(s).strip() for s in universe_raw.get("symbols", []))
        timeframe = str(universe_raw.get("timeframe", "1h"))
    else:
        raise StrategyParseError("'universe' must be list or mapping")
    if not symbols:
        raise StrategyParseError("'universe.symbols' is empty")

    indicators_raw = data.get("indicators", [])
    if not isinstance(indicators_raw, list):
        raise StrategyParseError("'indicators' must be a list")
    indicators: list[Indicator] = []
    for entry in indicators_raw:
        if not isinstance(entry, Mapping):
            raise StrategyParseError("indicator entries must be mappings")
        ind_name = str(entry["name"]).strip()
        alias = str(entry.get("alias", ind_name))
        params = {k: v for k, v in entry.items() if k not in {"name", "alias"}}
        indicators.append(Indicator(name=ind_name, alias=alias, params=params))

    rules: list[Rule] = []
    for r in data["rules"]:
        if not isinstance(r, Mapping):
            raise StrategyParseError("rule must be a mapping")
        when_raw = r.get("when")
        if not when_raw:
            raise StrategyParseError("rule missing 'when'")
        then_raw = str(r.get("then", "")).strip().lower()
        if then_raw not in {"buy", "sell", "close", "hold", "alert"}:
            raise StrategyParseError(f"unknown 'then' action: {then_raw}")
        size_expr = compile_expression(str(r["size"])) if r.get("size") is not None else None
        rules.append(
            Rule(
                when=compile_expression(str(when_raw)),
                then=then_raw,
                size=size_expr,
                note=str(r.get("note")) if r.get("note") else None,
            )
        )

    risk_raw = data.get("risk", {}) or {}
    if not isinstance(risk_raw, Mapping):
        raise StrategyParseError("'risk' must be a mapping")
    risk = RiskConfig(
        per_trade=float(risk_raw.get("per_trade", 0.02)),
        max_drawdown=float(risk_raw.get("max_drawdown", 0.5)),
        max_position_pct=float(risk_raw.get("max_position_pct", 0.5)),
        stop_loss_pct=_optional_float(risk_raw.get("stop_loss_pct")),
        take_profit_pct=_optional_float(risk_raw.get("take_profit_pct")),
        daily_loss_limit_pct=_optional_float(risk_raw.get("daily_loss_limit_pct")),
    )

    return StrategyDoc(
        name=name,
        universe=Universe(symbols=symbols, timeframe=timeframe),
        indicators=tuple(indicators),
        rules=tuple(rules),
        risk=risk,
        parameters=dict(data.get("parameters", {}) or {}),
        description=str(data["description"]) if data.get("description") else None,
    )


def _optional_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise StrategyParseError(f"expected number, got {value!r}") from exc
