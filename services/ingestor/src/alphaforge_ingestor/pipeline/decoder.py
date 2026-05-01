"""
Lightweight EVM log decoder for popular events.

The decoder maps topic[0] keccak hashes of well-known event signatures to
human readable names + decoded args. We intentionally stay small here — full
ABI decoding lives in the worker.
"""

from __future__ import annotations

from typing import Any

# keccak256 of canonical event signatures (precomputed)
EVENT_SIGNATURES: dict[str, str] = {
    "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef": "Transfer(address,address,uint256)",
    "0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925": "Approval(address,address,uint256)",
    "0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822": "Swap(address,uint256,uint256,uint256,uint256,address)",
    "0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67": "Swap(uint256,address,address,int256,int256,uint160,uint128,int24)",
    "0x4c209b5fc8ad50758f13e2e1088ba56a560dff690a1c6fef26394f4c03821c4f": "Mint(address,uint256,uint256)",
    "0xdccd412f0b1252819cb1fd330b93224ca42612892bb3f4f789976e6d81936496": "Burn(address,uint256,uint256,address)",
}


class EVMLogDecoder:
    """Tiny stateless decoder."""

    def try_decode(self, log_entry: dict[str, Any]) -> tuple[str | None, dict[str, Any] | None]:
        topics = log_entry.get("topics") or []
        if not topics:
            return None, None
        sig_hash = topics[0]
        sig = EVENT_SIGNATURES.get(sig_hash)
        if sig is None:
            return None, None
        # super-shallow arg parsing — only addresses inferred from indexed topics
        args: dict[str, Any] = {}
        for i, t in enumerate(topics[1:], start=1):
            if isinstance(t, str) and t.startswith("0x") and len(t) == 66:
                args[f"topic{i}"] = "0x" + t[-40:]
        return sig.split("(", 1)[0], args
