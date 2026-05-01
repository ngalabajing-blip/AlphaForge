from __future__ import annotations

import json
import os
from pathlib import Path

from alphaforge_cli.config import CLIConfig


def test_config_roundtrip(tmp_path: Path, monkeypatch) -> None:
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("ALPHAFORGE_HOME", str(home / ".alphaforge"))
    cfg = CLIConfig(
        api_url="http://api.example.com",
        api_key="afk_test",
        access_token="tok",
        refresh_token="ref",
        default_symbol="BTC/USDT",
        default_chain="bsc",
    )
    cfg.save()
    loaded = CLIConfig.load()
    assert loaded.api_url == "http://api.example.com"
    assert loaded.api_key == "afk_test"
    assert loaded.access_token == "tok"
    assert loaded.refresh_token == "ref"
    assert loaded.default_symbol == "BTC/USDT"
    assert loaded.default_chain == "bsc"


def test_config_env_overrides(tmp_path: Path, monkeypatch) -> None:
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("ALPHAFORGE_HOME", str(home / ".alphaforge"))
    monkeypatch.setenv("ALPHAFORGE_API_URL", "http://override.example.com")
    monkeypatch.setenv("ALPHAFORGE_API_KEY", "afk_env")
    cfg = CLIConfig.load()
    assert cfg.api_url == "http://override.example.com"
    assert cfg.api_key == "afk_env"


def test_config_partial_save(tmp_path: Path, monkeypatch) -> None:
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("ALPHAFORGE_HOME", str(home / ".alphaforge"))
    cfg = CLIConfig()
    cfg.api_url = "http://mocked"
    cfg.save()
    raw = json.loads((home / ".alphaforge" / "config.json").read_text())
    assert raw["api_url"] == "http://mocked"
