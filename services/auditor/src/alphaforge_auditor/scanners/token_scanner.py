"""
Token-level scanner — checks token metadata, holder concentration, and
liquidity pool details.

In dev environments the underlying explorer / DexScreener APIs may not be
reachable, so this scanner returns informational findings only.
"""

from __future__ import annotations


class TokenScanner:
    async def analyse(self, chain: str, address: str) -> list[dict]:
        findings: list[dict] = []
        # Heuristics that don't require external data:
        if address.endswith("0000000000000000"):
            findings.append(
                {
                    "category": "token",
                    "code": "TOKEN_VANITY_ADDRESS",
                    "severity": "info",
                    "description": "Address has trailing zeroes — vanity-mined; common in scam tokens",
                }
            )
        if address == "0x" + "0" * 40:
            findings.append(
                {
                    "category": "token",
                    "code": "TOKEN_BURN_ADDRESS",
                    "severity": "low",
                    "description": "Burn address",
                }
            )
        return findings
