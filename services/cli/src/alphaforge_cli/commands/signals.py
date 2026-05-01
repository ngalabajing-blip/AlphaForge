from __future__ import annotations

import json

import typer
import websockets  # type: ignore[import-not-found]
from rich.console import Console

from alphaforge_cli.config import CLIConfig

signals_app = typer.Typer(no_args_is_help=True)
console = Console()


@signals_app.command("stream")
def stream() -> None:
    """Subscribe to live signals over WebSocket."""
    import asyncio
    asyncio.run(_stream())


async def _stream() -> None:
    config = CLIConfig.load()
    url = config.api_url.rstrip("/").replace("http", "ws") + "/ws/signals"
    if config.access_token:
        url += f"?token={config.access_token}"
    async with websockets.connect(url) as ws:
        while True:
            try:
                msg = await ws.recv()
            except Exception as exc:  # noqa: BLE001
                console.print(f"[red]disconnected:[/red] {exc}")
                break
            try:
                data = json.loads(msg)
            except Exception:
                console.print(msg)
                continue
            console.print_json(data=data)


@signals_app.command("recent")
def recent(strategy_id: str = typer.Option(None), limit: int = typer.Option(50)) -> None:
    """Show the most recent signals."""
    from alphaforge_cli.client import APIClient
    params: dict = {"limit": limit}
    if strategy_id:
        params["strategy_id"] = strategy_id
    with APIClient() as client:
        resp = client.get("/api/v1/signals", params=params)
    console.print_json(data=resp)
