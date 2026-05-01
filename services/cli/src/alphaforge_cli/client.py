"""Thin HTTP client wrapping the AlphaForge REST API."""
from __future__ import annotations

import httpx

from alphaforge_cli.config import CLIConfig


class APIClient:
    def __init__(self, config: CLIConfig | None = None) -> None:
        self.config = config or CLIConfig.load()
        headers: dict[str, str] = {"Accept": "application/json"}
        if self.config.access_token:
            headers["Authorization"] = f"Bearer {self.config.access_token}"
        if self.config.api_key:
            headers["X-API-Key"] = self.config.api_key
        self.http = httpx.Client(base_url=self.config.api_url, headers=headers, timeout=15.0)

    def __enter__(self) -> "APIClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # type: ignore[no-untyped-def]
        self.http.close()

    def get(self, path: str, **kwargs) -> dict:  # type: ignore[no-untyped-def]
        r = self.http.get(path, **kwargs)
        r.raise_for_status()
        return r.json() if r.content else {}

    def post(self, path: str, **kwargs) -> dict:  # type: ignore[no-untyped-def]
        r = self.http.post(path, **kwargs)
        r.raise_for_status()
        return r.json() if r.content else {}

    def patch(self, path: str, **kwargs) -> dict:  # type: ignore[no-untyped-def]
        r = self.http.patch(path, **kwargs)
        r.raise_for_status()
        return r.json() if r.content else {}

    def delete(self, path: str, **kwargs) -> None:  # type: ignore[no-untyped-def]
        r = self.http.delete(path, **kwargs)
        r.raise_for_status()
