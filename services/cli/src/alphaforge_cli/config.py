"""CLI configuration — loads from env + ~/.alphaforge/config.json."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, fields
from pathlib import Path


def _config_dir() -> Path:
    return Path(os.environ.get("ALPHAFORGE_HOME", str(Path.home() / ".alphaforge")))


def _config_file() -> Path:
    return _config_dir() / "config.json"


# Kept for backwards compatibility — these reflect the env at *import time*.
CONFIG_DIR = _config_dir()
CONFIG_FILE = _config_file()


@dataclass
class CLIConfig:
    api_url: str = "http://localhost:8000"
    api_key: str | None = None
    access_token: str | None = None
    refresh_token: str | None = None
    default_symbol: str = "ETH/USDT"
    default_chain: str = "eth"

    @classmethod
    def load(cls) -> CLIConfig:
        path = _config_file()
        defaults = cls()
        # File overrides defaults; env then overrides file.
        merged: dict[str, object] = {f.name: getattr(defaults, f.name) for f in fields(cls)}
        if path.exists():
            try:
                data = json.loads(path.read_text())
                if isinstance(data, dict):
                    for f in fields(cls):
                        if f.name in data:
                            merged[f.name] = data[f.name]
            except Exception:
                pass
        env_map = {
            "api_url": "ALPHAFORGE_API_URL",
            "api_key": "ALPHAFORGE_API_KEY",
            "access_token": "ALPHAFORGE_TOKEN",
            "refresh_token": "ALPHAFORGE_REFRESH_TOKEN",
            "default_symbol": "ALPHAFORGE_DEFAULT_SYMBOL",
            "default_chain": "ALPHAFORGE_DEFAULT_CHAIN",
        }
        for attr, var in env_map.items():
            if var in os.environ:
                merged[attr] = os.environ[var]
        return cls(**merged)  # type: ignore[arg-type]

    def save(self) -> None:
        d = _config_dir()
        d.mkdir(parents=True, exist_ok=True)
        (d / "config.json").write_text(json.dumps(asdict(self), indent=2))
