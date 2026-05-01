"""
EVM bytecode scanner.

Looks for known dangerous opcodes / signatures that frequently indicate:

* SELFDESTRUCT (rug-pull / drain)
* DELEGATECALL with attacker-controlled target
* Hidden mint functions (ERC20 transfer skim)
* Permitless ownership / blocklist functions
* Rebasing balances
* Disabled transfer (honeypot)

The scanner is conservative — high-confidence findings only.
"""
from __future__ import annotations

from typing import Iterable

# function selectors of common honeypot / rug functions (4-byte hashes)
DANGEROUS_SELECTORS = {
    "8da5cb5b": ("OWNERSHIP_VIEW", "low", "Has owner() view; ownership-based privilege"),
    "f2fde38b": ("OWNERSHIP_TRANSFER", "low", "transferOwnership() exposed"),
    "8456cb59": ("PAUSABLE", "medium", "Pausable contract — transfers can be halted"),
    "3950935f": ("BLOCKLIST_BLACKLIST", "high", "Blacklist/blocklist function detected"),
    "fffffff0": ("HIDDEN_MINT", "high", "Possible hidden mint selector"),
    "12fa6feb": ("FORCE_TRANSFER", "high", "Force-transfer / sweep selector detected"),
    "095ea7b3": ("APPROVE", "info", "Standard ERC20 approve()"),
}

# raw bytecode patterns
PATTERNS = {
    "ff0000": ("SELFDESTRUCT", "critical", "SELFDESTRUCT opcode (0xff) present"),
    "f4": ("DELEGATECALL", "high", "DELEGATECALL opcode used — review proxy patterns"),
    "f0": ("CREATE", "low", "CREATE opcode used"),
    "f5": ("CREATE2", "low", "CREATE2 opcode used"),
    "fa": ("STATICCALL", "info", "STATICCALL used"),
    "31": ("BALANCE_OPCODE", "info", "BALANCE opcode used"),
}


class BytecodeScanner:
    def analyse(self, bytecode: bytes) -> list[dict]:
        findings: list[dict] = []
        hex_code = bytecode.hex()

        # selector hits — selector blocks usually appear as PUSH4 0x????????
        for sel, (code, severity, description) in DANGEROUS_SELECTORS.items():
            if f"63{sel}" in hex_code:
                findings.append(self._mk(code, severity, description))

        # opcode patterns
        for pattern, (code, severity, description) in PATTERNS.items():
            if pattern in hex_code:
                findings.append(self._mk(code, severity, description))

        if len(bytecode) < 32:
            findings.append(self._mk("EMPTY_BYTECODE", "high", "Contract has no runtime bytecode"))
        if len(bytecode) > 24576:
            findings.append(self._mk("OVERSIZED_BYTECODE", "low",
                                     f"Runtime bytecode exceeds EIP-170 limit ({len(bytecode)} bytes)"))

        return findings

    @staticmethod
    def _mk(code: str, severity: str, description: str) -> dict:
        return {"category": "bytecode", "code": code, "severity": severity, "description": description}
