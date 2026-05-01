from __future__ import annotations

import typer
from rich.console import Console

from alphaforge_cli.client import APIClient
from alphaforge_cli.config import CLIConfig

auth_app = typer.Typer(no_args_is_help=True)
console = Console()


@auth_app.command("login")
def login(email: str = typer.Option(...), password: str = typer.Option(..., prompt=True, hide_input=True)) -> None:
    """Log in and persist access tokens locally."""
    config = CLIConfig.load()
    with APIClient(config) as client:
        resp = client.post("/api/v1/auth/token", data={"username": email, "password": password})
    config.access_token = resp.get("access_token")
    config.refresh_token = resp.get("refresh_token")
    config.save()
    console.print(f"[green]✓[/green] logged in as {email}")


@auth_app.command("whoami")
def whoami() -> None:
    """Print the currently authenticated user."""
    with APIClient() as client:
        me = client.get("/api/v1/users/me")
    console.print_json(data=me)


@auth_app.command("logout")
def logout() -> None:
    """Forget the persisted tokens."""
    config = CLIConfig.load()
    config.access_token = None
    config.refresh_token = None
    config.save()
    console.print("[yellow]session cleared[/yellow]")
