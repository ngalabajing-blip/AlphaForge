from datetime import UTC, datetime
from decimal import Decimal

from alphaforge_worker.runtime.portfolio import Portfolio


def _now():
    return datetime.now(tz=UTC)


def test_buy_reduces_cash():
    p = Portfolio(cash=Decimal("10000"))
    p.buy("ETH", Decimal("100"), Decimal("10"), _now())
    assert p.cash < Decimal("10000")
    assert p.positions["ETH"].quantity == Decimal("10")


def test_sell_realises_pnl():
    p = Portfolio(cash=Decimal("10000"))
    p.buy("ETH", Decimal("100"), Decimal("10"), _now())
    fill = p.sell("ETH", Decimal("110"), Decimal("10"), _now())
    assert fill.pnl > 0


def test_drawdown_tracking():
    p = Portfolio(cash=Decimal("1000"))
    p.mark(_now(), {})
    p.cash = Decimal("1500")
    p.mark(_now(), {})
    p.cash = Decimal("900")
    p.mark(_now(), {})
    assert p.drawdown > 0
