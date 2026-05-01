from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from alphaforge_cli.client import APIClient

chains_app = typer.Typer(no_args_is_help=True)
console = Console()


@chains_app.command("list")
def list_chains() -> None:
    with APIClient() as client:
        resp = client.get("/api/v1/chains")
    table = Table(title="Supported Chains")
    for col in ("Name", "Chain ID", "Family", "Currency", "Has WS"):
        table.add_column(col)
    for c in resp.get("chains", []):
        table.add_row(
            c["name"],
            str(c.get("chain_id") or "-"),
            c.get("family", ""),
            c.get("native_currency", ""),
            "yes" if c.get("has_ws") else "no",
        )
    console.print(table)
