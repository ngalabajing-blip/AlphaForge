"""Typer entrypoint."""
from __future__ import annotations

import typer

from alphaforge_cli.commands import (
    auth_app,
    audits_app,
    backtests_app,
    market_app,
    signals_app,
    strategies_app,
    chains_app,
)

app = typer.Typer(
    name="alphaforge",
    help="AlphaForge command-line client.",
    no_args_is_help=True,
    add_completion=False,
)
app.add_typer(auth_app, name="auth", help="Authenticate against the API")
app.add_typer(strategies_app, name="strategies", help="Manage strategies")
app.add_typer(backtests_app, name="backtests", help="Run and inspect backtests")
app.add_typer(signals_app, name="signals", help="Stream and inspect signals")
app.add_typer(audits_app, name="audits", help="Smart contract audits")
app.add_typer(market_app, name="market", help="Market data utilities")
app.add_typer(chains_app, name="chains", help="On-chain helpers")


@app.command()
def version() -> None:
    from alphaforge_cli import __version__
    typer.echo(f"alphaforge-cli {__version__}")


if __name__ == "__main__":
    app()
