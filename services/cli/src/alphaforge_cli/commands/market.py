from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from alphaforge_cli.client import APIClient

market_app = typer.Typer(no_args_is_help=True)
console = Console()


@market_app.command("ticker")
def ticker(symbol: str = typer.Argument("ETH/USDT")) -> None:
    """Show the latest price tick."""
    with APIClient() as client:
        resp = client.get(f"/api/v1/market/ticker/{symbol}")
    console.print_json(data=resp)


@market_app.command("candles")
def candles(symbol: str, timeframe: str = typer.Option("1h"), limit: int = typer.Option(50)) -> None:
    with APIClient() as client:
        resp = client.get(
            f"/api/v1/market/candles/{symbol}",
            params={"timeframe": timeframe, "limit": limit},
        )
    table = Table(title=f"{symbol} {timeframe}")
    for col in ("ts", "open", "high", "low", "close", "volume"):
        table.add_column(col)
    for c in resp.get("candles", []):
        table.add_row(
            c["ts"],
            str(c["open"]),
            str(c["high"]),
            str(c["low"]),
            str(c["close"]),
            str(c["volume"]),
        )
    console.print(table)


@market_app.command("dominance")
def dominance(quote: str = typer.Option("USDT")) -> None:
    with APIClient() as client:
        resp = client.get("/api/v1/market/dominance", params={"quote": quote})
    console.print_json(data=resp)


@market_app.command("movers")
def movers(direction: str = typer.Option("up"), n: int = typer.Option(10)) -> None:
    with APIClient() as client:
        resp = client.get("/api/v1/market/movers", params={"direction": direction, "n": n})
    console.print_json(data=resp)
