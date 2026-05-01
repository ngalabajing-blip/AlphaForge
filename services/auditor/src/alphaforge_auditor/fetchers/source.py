"""Fetch verified source code from explorer APIs."""
from __future__ import annotations

from alphaforge_auditor.config import get_settings


class SourceFetcher:
    EXPLORER = {
        "eth": ("https://api.etherscan.io/api", "etherscan"),
        "bsc": ("https://api.bscscan.com/api", "bsc"),
        "polygon": ("https://api.polygonscan.com/api", "polygon"),
        "arbitrum": ("https://api.arbiscan.io/api", "arb"),
        "base": ("https://api.basescan.org/api", "base"),
        "optimism": ("https://api-optimistic.etherscan.io/api", "op"),
        "avalanche": ("https://api.snowtrace.io/api", "avax"),
    }

    def __init__(self, http) -> None:  # type: ignore[no-untyped-def]
        self._http = http

    async def fetch(self, chain: str, address: str) -> dict | None:
        entry = self.EXPLORER.get(chain)
        if entry is None:
            return None
        url, key_name = entry
        api_key = self._api_key(key_name)
        params = {"module": "contract", "action": "getsourcecode", "address": address}
        if api_key:
            params["apikey"] = api_key
        try:
            r = await self._http.get(url, params=params)
            r.raise_for_status()
            payload = r.json()
            result = payload.get("result")
            if not result:
                return None
            entry = result[0] if isinstance(result, list) and result else None
            if not entry:
                return None
            return {
                "source_code": entry.get("SourceCode") or "",
                "abi": entry.get("ABI") or "",
                "contract_name": entry.get("ContractName") or "",
                "compiler": entry.get("CompilerVersion") or "",
                "is_verified": bool(entry.get("SourceCode")),
            }
        except Exception:
            return None

    @staticmethod
    def _api_key(name: str) -> str | None:
        settings = get_settings()
        return {
            "etherscan": settings.etherscan_api_key,
            "bsc": settings.bscscan_api_key,
            "polygon": settings.polygonscan_api_key,
            "arb": settings.arbiscan_api_key,
            "base": settings.basescan_api_key,
            "op": settings.optimism_api_key,
            "avax": settings.snowtrace_api_key,
        }.get(name)
