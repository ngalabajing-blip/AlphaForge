"""Risk manager — rejects orders that violate strategy / global risk limits."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from alphaforge_worker.dsl.ast import RiskConfig
from alphaforge_worker.runtime.portfolio import Portfolio


@dataclass
class RiskDecision:
    allowed: bool
    reason: str | None = None
    adjusted_quantity: Decimal | None = None


class RiskManager:
    def __init__(self, risk: RiskConfig, equity_at_start: Decimal) -> None:
        self.risk = risk
        self.equity_start = equity_at_start
        self.daily_loss_marker: Decimal = equity_at_start
        self.daily_marker_date: str | None = None

    def check(
        self,
        *,
        ts: datetime,
        symbol: str,
        side: str,
        price: Decimal,
        quantity: Decimal,
        portfolio: Portfolio,
        marks: dict[str, Decimal],
    ) -> RiskDecision:
        equity = portfolio.equity(marks)
        if portfolio.drawdown > Decimal(str(self.risk.max_drawdown)):
            return RiskDecision(False, f"max_drawdown_exceeded:{portfolio.drawdown:.2%}")

        if side == "buy":
            notional = price * quantity
            equity = max(equity, Decimal("1"))
            position_value = portfolio.positions.get(symbol)
            current_value = (position_value.quantity * price) if position_value else Decimal("0")
            if (current_value + notional) > equity * Decimal(str(self.risk.max_position_pct)):
                cap = equity * Decimal(str(self.risk.max_position_pct)) - current_value
                if cap <= 0:
                    return RiskDecision(False, "position_cap_reached")
                qty = cap / price
                return RiskDecision(True, "trimmed_to_position_cap", adjusted_quantity=qty)

        # daily loss limit
        if self.risk.daily_loss_limit_pct is not None:
            today = ts.strftime("%Y-%m-%d")
            if today != self.daily_marker_date:
                self.daily_marker_date = today
                self.daily_loss_marker = equity
            loss = self.daily_loss_marker - equity
            if loss > self.daily_loss_marker * Decimal(str(self.risk.daily_loss_limit_pct)):
                return RiskDecision(False, "daily_loss_limit_hit")

        return RiskDecision(True)
