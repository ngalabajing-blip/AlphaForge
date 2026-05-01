from __future__ import annotations

import os

import httpx
import pytest


@pytest.fixture(scope="session")
def base_url() -> str:
    return os.environ.get("ALPHAFORGE_E2E_URL", "http://localhost:8000")


@pytest.fixture(scope="session")
def client(base_url: str) -> httpx.Client:
    return httpx.Client(base_url=base_url, timeout=30.0)


@pytest.fixture(scope="session")
def access_token(client: httpx.Client) -> str:
    resp = client.post(
        "/api/v1/auth/token",
        data={"username": "admin@alphaforge.local", "password": "changeme"},
    )
    if resp.status_code != 200:
        pytest.skip("API not available; skipping E2E suite")
    return resp.json()["access_token"]


@pytest.fixture()
def auth_client(client: httpx.Client, access_token: str) -> httpx.Client:
    client.headers.update({"Authorization": f"Bearer {access_token}"})
    return client
