from __future__ import annotations

from pathlib import Path

import typer
import yaml
from rich.console import Console
from rich.table import Table

from alphaforge_cli.client import APIClient

strategies_app = typer.Typer(no_args_is_help=True)
console = Console()


@strategies_app.command("list")
def list_strategies() -> None:
    """List your strategies (and public ones)."""
    with APIClient() as client:
        page = client.get("/api/v1/strategies")
    table = Table(title="Strategies")
    for col in ("ID", "Name", "Public", "Versions", "Tags"):
        table.add_column(col)
    for item in page.get("items", []):
        table.add_row(
            item["id"][:8],
            item["name"],
            "yes" if item.get("is_public") else "no",
            str(item.get("latest_version", 0)),
            ",".join(item.get("tags") or []),
        )
    console.print(table)


@strategies_app.command("create")
def create(
    name: str = typer.Option(...),
    file: Path = typer.Option(..., exists=True, readable=True),
    public: bool = typer.Option(False, "--public/--private"),
    tags: str = typer.Option("", help="comma-separated"),
) -> None:
    """Create a new strategy from a YAML file."""
    raw = file.read_text()
    payload = {
        "name": name,
        "is_public": public,
        "tags": [t.strip() for t in tags.split(",") if t.strip()],
        "raw_source": raw,
        "parameters": _parse_parameters(raw),
    }
    with APIClient() as client:
        resp = client.post("/api/v1/strategies", json=payload)
    console.print_json(data=resp)


@strategies_app.command("show")
def show(strategy_id: str) -> None:
    with APIClient() as client:
        resp = client.get(f"/api/v1/strategies/{strategy_id}")
    console.print_json(data=resp)


@strategies_app.command("delete")
def delete(strategy_id: str) -> None:
    with APIClient() as client:
        client.delete(f"/api/v1/strategies/{strategy_id}")
    console.print(f"[red]archived {strategy_id}[/red]")


@strategies_app.command("publish-version")
def publish_version(
    strategy_id: str,
    file: Path = typer.Option(..., exists=True, readable=True),
    notes: str = typer.Option("", "--notes"),
) -> None:
    raw = file.read_text()
    payload = {"raw_source": raw, "parameters": _parse_parameters(raw), "notes": notes or None}
    with APIClient() as client:
        resp = client.post(f"/api/v1/strategies/{strategy_id}/versions", json=payload)
    console.print_json(data=resp)


def _parse_parameters(raw: str) -> dict:
    try:
        data = yaml.safe_load(raw)
        if isinstance(data, dict):
            params = data.get("parameters") or {}
            if isinstance(params, dict):
                return params
    except Exception:
        pass
    return {}
