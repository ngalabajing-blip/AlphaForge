from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from alphaforge_cli.client import APIClient

audits_app = typer.Typer(no_args_is_help=True)
console = Console()


@audits_app.command("request")
def request(address: str, chain: str = typer.Option("eth"), deep: bool = typer.Option(True, "--deep/--shallow")) -> None:
    """Request a smart contract audit."""
    with APIClient() as client:
        resp = client.post("/api/v1/audits", json={"address": address, "chain": chain, "deep": deep})
    console.print_json(data=resp)


@audits_app.command("show")
def show(job_id: str) -> None:
    """Show the result of an audit job."""
    with APIClient() as client:
        resp = client.get(f"/api/v1/audits/{job_id}")
    console.print_json(data=resp)


@audits_app.command("list")
def list_audits(address: str = typer.Option(None)) -> None:
    """List recent audit jobs."""
    params = {"address": address} if address else None
    with APIClient() as client:
        resp = client.get("/api/v1/audits", params=params)
    table = Table(title="Recent Audits")
    for col in ("ID", "Chain", "Address", "Status", "Risk", "Severity"):
        table.add_column(col)
    for item in resp.get("items", []):
        table.add_row(
            item["id"][:8],
            item.get("chain", ""),
            item.get("address", "")[:12] + "…",
            item.get("status", ""),
            str(item.get("risk_score", "")),
            item.get("risk_level", ""),
        )
    console.print(table)
