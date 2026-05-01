"""Backtest metrics — Sharpe, Sortino, win-rate, drawdown."""
from __future__ import annotations

import math
from dataclasses import dataclass
from decimal import Decimal
from typing import Sequence


@dataclass
class BacktestMetrics:
    initial_balance: Decimal
    final_balance: Decimal
    pnl_abs: Decimal
    pnl_pct: Decimal
    sharpe: Decimal
    sortino: Decimal
    max_drawdown: Decimal
    win_rate: Decimal
    trades_count: int
    metrics: dict


def compute_metrics(
    *,
    initial: Decimal,
    equity_curve: Sequence[tuple[object, Decimal]],
    trade_pnls: Sequence[Decimal],
) -> BacktestMetrics:
    final = equity_curve[-1][1] if equity_curve else initial
    pnl_abs = final - initial
    pnl_pct = (pnl_abs / initial) * Decimal("100") if initial else Decimal("0")

    returns: list[float] = []
    for i in range(1, len(equity_curve)):
        prev = float(equity_curve[i - 1][1])
        curr = float(equity_curve[i][1])
        if prev > 0:
            returns.append((curr - prev) / prev)

    sharpe = _annualised_sharpe(returns)
    sortino = _annualised_sortino(returns)
    max_dd = _max_drawdown(equity_curve)
    wins = sum(1 for p in trade_pnls if p > 0)
    losses = sum(1 for p in trade_pnls if p < 0)
    win_rate = (Decimal(wins) / Decimal(wins + losses) * Decimal("100")) if (wins + losses) else Decimal("0")

    extra = {
        "trades_total": len(trade_pnls),
        "wins": wins,
        "losses": losses,
        "best_trade": float(max(trade_pnls)) if trade_pnls else 0.0,
        "worst_trade": float(min(trade_pnls)) if trade_pnls else 0.0,
        "avg_return": float(sum(returns) / len(returns)) if returns else 0.0,
        "stdev_return": _stdev(returns),
    }
    return BacktestMetrics(
        initial_balance=initial,
        final_balance=final,
        pnl_abs=pnl_abs,
        pnl_pct=pnl_pct.quantize(Decimal("0.0001")),
        sharpe=Decimal(str(round(sharpe, 4))),
        sortino=Decimal(str(round(sortino, 4))),
        max_drawdown=max_dd,
        win_rate=win_rate.quantize(Decimal("0.0001")),
        trades_count=len(trade_pnls),
        metrics=extra,
    )


def _annualised_sharpe(returns: list[float], periods_per_year: int = 365 * 24) -> float:
    if len(returns) < 2:
        return 0.0
    mean = sum(returns) / len(returns)
    sd = _stdev(returns)
    if sd == 0:
        return 0.0
    return (mean / sd) * math.sqrt(periods_per_year)


def _annualised_sortino(returns: list[float], periods_per_year: int = 365 * 24) -> float:
    if len(returns) < 2:
        return 0.0
    mean = sum(returns) / len(returns)
    downside = [r for r in returns if r < 0]
    if not downside:
        return 0.0
    sd = _stdev(downside)
    if sd == 0:
        return 0.0
    return (mean / sd) * math.sqrt(periods_per_year)


def _max_drawdown(equity_curve: Sequence[tuple[object, Decimal]]) -> Decimal:
    if not equity_curve:
        return Decimal("0")
    peak = equity_curve[0][1]
    max_dd = Decimal("0")
    for _, eq in equity_curve:
        peak = max(peak, eq)
        if peak > 0:
            dd = (peak - eq) / peak
            if dd > max_dd:
                max_dd = dd
    return max_dd.quantize(Decimal("0.0001"))


def _stdev(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    var = sum((v - mean) ** 2 for v in values) / (len(values) - 1)
    return math.sqrt(var)
