"""
In-memory portfolio used by the backtest engine and live runner.

Tracks balances, open positions, realised PnL, and produces a fill record per
order.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal


@dataclass
class Position:
    symbol: str
    quantity: Decimal = Decimal("0")
    avg_price: Decimal = Decimal("0")

    def is_flat(self) -> bool:
        return self.quantity == 0


@dataclass
class Fill:
    symbol: str
    side: str  # buy | sell
    price: Decimal
    quantity: Decimal
    fee: Decimal
    ts: datetime
    pnl: Decimal = Decimal("0")


@dataclass
class Portfolio:
    cash: Decimal
    fee_bps: Decimal = Decimal("10")
    slippage_bps: Decimal = Decimal("5")
    positions: dict[str, Position] = field(default_factory=dict)
    fills: list[Fill] = field(default_factory=list)
    equity_curve: list[tuple[datetime, Decimal]] = field(default_factory=list)
    high_water_mark: Decimal = Decimal("0")

    def equity(self, marks: dict[str, Decimal]) -> Decimal:
        total = self.cash
        for sym, pos in self.positions.items():
            if pos.is_flat():
                continue
            price = marks.get(sym, pos.avg_price)
            total += pos.quantity * price
        return total

    def buy(self, symbol: str, price: Decimal, quantity: Decimal, ts: datetime) -> Fill:
        slip = price * (Decimal("1") + self.slippage_bps / Decimal("10000"))
        notional = slip * quantity
        fee = notional * (self.fee_bps / Decimal("10000"))
        if notional + fee > self.cash:
            quantity = max(Decimal("0"), (self.cash * Decimal("0.999")) / slip)
            notional = slip * quantity
            fee = notional * (self.fee_bps / Decimal("10000"))
        self.cash -= notional + fee
        pos = self.positions.setdefault(symbol, Position(symbol=symbol))
        new_qty = pos.quantity + quantity
        if new_qty != 0:
            pos.avg_price = ((pos.avg_price * pos.quantity) + (slip * quantity)) / new_qty
        pos.quantity = new_qty
        fill = Fill(symbol, "buy", slip, quantity, fee, ts)
        self.fills.append(fill)
        return fill

    def sell(self, symbol: str, price: Decimal, quantity: Decimal, ts: datetime) -> Fill:
        slip = price * (Decimal("1") - self.slippage_bps / Decimal("10000"))
        notional = slip * quantity
        fee = notional * (self.fee_bps / Decimal("10000"))
        pos = self.positions.setdefault(symbol, Position(symbol=symbol))
        quantity = min(quantity, max(Decimal("0"), pos.quantity))
        notional = slip * quantity
        fee = notional * (self.fee_bps / Decimal("10000"))
        self.cash += notional - fee
        pnl = (slip - pos.avg_price) * quantity - fee
        pos.quantity -= quantity
        if pos.is_flat():
            pos.avg_price = Decimal("0")
        fill = Fill(symbol, "sell", slip, quantity, fee, ts, pnl=pnl)
        self.fills.append(fill)
        return fill

    def mark(self, ts: datetime, marks: dict[str, Decimal]) -> Decimal:
        eq = self.equity(marks)
        self.equity_curve.append((ts, eq))
        if eq > self.high_water_mark:
            self.high_water_mark = eq
        return eq

    @property
    def drawdown(self) -> Decimal:
        if not self.equity_curve:
            return Decimal("0")
        latest = self.equity_curve[-1][1]
        if self.high_water_mark == 0:
            return Decimal("0")
        return (self.high_water_mark - latest) / self.high_water_mark
