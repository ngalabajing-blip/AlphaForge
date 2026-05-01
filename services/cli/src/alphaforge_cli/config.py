"""CLI configuration — loads from env + ~/.alphaforge/config.toml."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from pathlib import Path

CONFIG_DIR = Path(os.environ.get("ALPHAFORGE_HOME", str(Path.home() / ".alphaforge")))
CONFIG_FILE = CONFIG_DIR / "config.json"


@dataclass
class CLIConfig:
    api_url: str = "http://localhost:8000"
    api_key: str | None = None
    access_token: str | None = None
    refresh_token: str | None = None
    default_symbol: str = "ETH/USDT"
    default_chain: str = "eth"

    @classmethod
    def load(cls) -> "CLIConfig":
        if CONFIG_FILE.exists():
            try:
                data = json.loads(CONFIG_FILE.read_text())
                return cls(**{k: data.get(k, getattr(cls(), k)) for k in cls().__dict__})
            except Exception:
                pass
        return cls(
            api_url=os.environ.get("ALPHAFORGE_API_URL", cls.api_url),
            api_key=os.environ.get("ALPHAFORGE_API_KEY"),
            access_token=os.environ.get("ALPHAFORGE_TOKEN"),
            default_symbol=os.environ.get("ALPHAFORGE_DEFAULT_SYMBOL", cls.default_symbol),
            default_chain=os.environ.get("ALPHAFORGE_DEFAULT_CHAIN", cls.default_chain),
        )

    def save(self) -> None:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        CONFIG_FILE.write_text(json.dumps(asdict(self), indent=2))
