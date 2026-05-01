"""Fetch raw bytecode via JSON-RPC."""

from __future__ import annotations

from alphaforge_shared.chains import CHAINS


class BytecodeFetcher:
    def __init__(self, http) -> None:  # type: ignore[no-untyped-def]
        self._http = http

    async def fetch(self, chain: str, address: str) -> bytes | None:
        spec = next((c for c in CHAINS if c.name == chain), None)
        if spec is None or not spec.rpc_url:
            return None
        try:
            r = await self._http.post(
                spec.rpc_url,
                json={
                    "jsonrpc": "2.0",
                    "method": "eth_getCode",
                    "params": [address, "latest"],
                    "id": 1,
                },
            )
            r.raise_for_status()
            data = r.json()
            code = (data.get("result") or "0x").removeprefix("0x")
            if not code or code == "0":
                return None
            return bytes.fromhex(code)
        except Exception:
            return None
