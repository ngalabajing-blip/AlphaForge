from datetime import UTC, datetime, timedelta
from decimal import Decimal

from alphaforge_worker.runtime.metrics import compute_metrics


def test_winning_curve():
    now = datetime.now(tz=UTC)
    curve = [(now + timedelta(hours=i), Decimal(str(1000 + i * 5))) for i in range(50)]
    metrics = compute_metrics(
        initial=Decimal("1000"),
        equity_curve=curve,
        trade_pnls=[Decimal("5"), Decimal("-2"), Decimal("10")],
    )
    assert metrics.pnl_abs > 0
    assert metrics.win_rate > 0
    assert metrics.max_drawdown >= 0


def test_empty_curve():
    metrics = compute_metrics(initial=Decimal("1000"), equity_curve=[], trade_pnls=[])
    assert metrics.pnl_abs == 0
