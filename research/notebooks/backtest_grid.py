"""
Parameter-sweep backtests for the EMA cross strategy. Stores final
PnL + Sharpe per (fast, slow) combination as CSV. Useful for
visual heatmap plotting offline.
"""
from __future__ import annotations

import csv
import math
import random
from pathlib import Path


def _generate_candles(n: int, seed: int = 1) -> list[dict]:
    rng = random.Random(seed)
    price = 100.0
    out = []
    for i in range(n):
        drift = math.sin(i / 24) * 0.001
        shock = rng.gauss(0, 0.005)
        price = max(0.01, price * (1 + drift + shock))
        out.append({"close": price})
    return out


def _ema(values: list[float], period: int) -> list[float]:
    if not values:
        return []
    k = 2.0 / (period + 1.0)
    out = [values[0]]
    for v in values[1:]:
        out.append(out[-1] + k * (v - out[-1]))
    return out


def _backtest(closes: list[float], fast: int, slow: int) -> tuple[float, float]:
    fast_ema = _ema(closes, fast)
    slow_ema = _ema(closes, slow)
    cash = 1000.0
    qty = 0.0
    returns: list[float] = []
    prev_equity = cash
    in_position = False
    for i in range(1, len(closes)):
        cu = fast_ema[i] > slow_ema[i] and fast_ema[i - 1] <= slow_ema[i - 1]
        cd = fast_ema[i] < slow_ema[i] and fast_ema[i - 1] >= slow_ema[i - 1]
        if cu and not in_position:
            qty = (cash * 0.95) / closes[i]
            cash -= qty * closes[i]
            in_position = True
        elif cd and in_position:
            cash += qty * closes[i]
            qty = 0.0
            in_position = False
        equity = cash + qty * closes[i]
        ret = (equity - prev_equity) / prev_equity if prev_equity > 0 else 0.0
        returns.append(ret)
        prev_equity = equity
    final_equity = cash + qty * closes[-1]
    pnl = (final_equity - 1000.0) / 1000.0
    if not returns:
        return pnl, 0.0
    mean = sum(returns) / len(returns)
    var = sum((r - mean) ** 2 for r in returns) / max(1, len(returns) - 1)
    sd = math.sqrt(var)
    sharpe = 0.0 if sd == 0 else mean / sd * math.sqrt(252 * 24)
    return pnl, sharpe


def main() -> None:
    candles = _generate_candles(2000)
    closes = [c["close"] for c in candles]
    grid = []
    for fast in range(5, 41, 5):
        for slow in range(20, 101, 10):
            if fast >= slow:
                continue
            pnl, sharpe = _backtest(closes, fast, slow)
            grid.append({"fast": fast, "slow": slow, "pnl": pnl, "sharpe": sharpe})
    out_dir = Path(__file__).resolve().parent.parent / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "ema_grid.csv"
    with out_path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["fast", "slow", "pnl", "sharpe"])
        writer.writeheader()
        writer.writerows(grid)
    grid.sort(key=lambda r: r["sharpe"], reverse=True)
    print("top 5 by Sharpe:")
    for row in grid[:5]:
        print(row)


if __name__ == "__main__":
    main()
