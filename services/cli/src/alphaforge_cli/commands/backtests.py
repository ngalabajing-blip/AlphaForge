from __future__ import annotations

from datetime import UTC, datetime, timedelta

import typer
from rich.console import Console
from rich.table import Table

from alphaforge_cli.client import APIClient

backtests_app = typer.Typer(no_args_is_help=True)
console = Console()


@backtests_app.command("run")
def run(
    strategy_id: str,
    version: int = typer.Option(..., "--version", "-v"),
    days: int = typer.Option(30, "--days"),
    timeframe: str = typer.Option("1h"),
    initial_balance: float = typer.Option(10000.0),
    fee_bps: int = typer.Option(10),
    slippage_bps: int = typer.Option(5),
) -> None:
    """Enqueue a backtest."""
    end = datetime.now(tz=UTC).replace(microsecond=0)
    start = end - timedelta(days=days)
    payload = {
        "strategy_id": strategy_id,
        "strategy_version": version,
        "start_at": start.isoformat(),
        "end_at": end.isoformat(),
        "timeframe": timeframe,
        "initial_balance": initial_balance,
        "fee_bps": fee_bps,
        "slippage_bps": slippage_bps,
    }
    with APIClient() as client:
        resp = client.post("/api/v1/backtests", json=payload)
    console.print_json(data=resp)


@backtests_app.command("list")
def list_backtests(strategy_id: str = typer.Option(None)) -> None:
    params = {"strategy_id": strategy_id} if strategy_id else None
    with APIClient() as client:
        page = client.get("/api/v1/backtests", params=params)
    table = Table(title="Backtests")
    for col in (
        "ID",
        "Strategy",
        "Version",
        "Status",
        "PnL %",
        "Sharpe",
        "MaxDD",
        "Trades",
    ):
        table.add_column(col)
    for item in page.get("items", []):
        table.add_row(
            item["id"][:8],
            item.get("strategy_id", "")[:8],
            str(item.get("strategy_version", "")),
            item.get("status", ""),
            str(item.get("pnl_pct", "")),
            str(item.get("sharpe", "")),
            str(item.get("max_drawdown", "")),
            str(item.get("trades_count", "")),
        )
    console.print(table)


@backtests_app.command("show")
def show(backtest_id: str) -> None:
    with APIClient() as client:
        resp = client.get(f"/api/v1/backtests/{backtest_id}")
    console.print_json(data=resp)


@backtests_app.command("cancel")
def cancel(backtest_id: str) -> None:
    with APIClient() as client:
        client.delete(f"/api/v1/backtests/{backtest_id}")
    console.print(f"[red]cancelled {backtest_id}[/red]")
