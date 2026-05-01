"""
Solidity source heuristic scanner.

Pattern-based — *not* a full parser. Catches the long tail of obviously
unsafe constructs that show up in copy-paste rug pulls.
"""
from __future__ import annotations

import re

PATTERNS: list[tuple[str, str, str, str]] = [
    # (regex, code, severity, description)
    (r"selfdestruct\s*\(", "SOL_SELFDESTRUCT", "critical", "selfdestruct() found in source"),
    (r"\.delegatecall\s*\(", "SOL_DELEGATECALL", "high", "delegatecall() with potential attacker-controlled target"),
    (r"tx\.origin", "SOL_TX_ORIGIN", "high", "tx.origin used for authorisation — phishing vector"),
    (r"\bonlyOwner\b", "SOL_ONLY_OWNER", "info", "onlyOwner modifier present"),
    (r"function\s+mint\s*\(", "SOL_PUBLIC_MINT", "medium", "Public mint() function — potential supply inflation"),
    (r"function\s+blacklist\s*\(", "SOL_BLACKLIST", "high", "Blacklist function present"),
    (r"function\s+addToBlacklist\s*\(", "SOL_BLACKLIST", "high", "Blacklist add function present"),
    (r"function\s+setFee\s*\(", "SOL_FEE_FUNCTION", "medium", "Mutable fee setter present"),
    (r"function\s+pause\s*\(", "SOL_PAUSABLE", "medium", "Pausable transfer logic"),
    (r"_balances\[\w+\]\s*=\s*\d", "SOL_FORCE_BALANCE", "critical", "Direct balance manipulation in source"),
    (r"require\s*\(\s*sender\s*==\s*owner", "SOL_OWNER_GUARD", "info", "Owner-only sender guard"),
    (r"\.transfer\s*\(\s*\d+\s*\)", "SOL_HARDCODED_TRANSFER", "low", "Hard-coded transfer amount"),
    (r"abi\.encodePacked\s*\(", "SOL_ENCODE_PACKED", "info", "abi.encodePacked() used (collision risk)"),
    (r"unchecked\s*\{", "SOL_UNCHECKED_BLOCK", "info", "unchecked block — overflow review"),
    (r"\bfallback\s*\(\s*\)\s*external", "SOL_FALLBACK", "info", "Custom fallback() function"),
    (r"\breceive\s*\(\s*\)\s*external\s*payable", "SOL_RECEIVE", "info", "Custom receive() function"),
    (r"\bnew\s+\w+\s*\(", "SOL_NEW_DEPLOY", "info", "Deploys child contracts via 'new'"),
    (r"keccak256\s*\(\s*abi\.encodePacked\s*\(\s*[^,]*,[^,]*,[^,]*\)\)", "SOL_KECCAK_PACKED_MULTI",
     "medium", "keccak256(encodePacked(multiple args)) — collision risk"),
]


class SourceScanner:
    def analyse(self, source_code: str) -> list[dict]:
        findings: list[dict] = []
        if not source_code:
            return findings
        # Solidity source from explorers is sometimes wrapped in `{{ ... }}`
        # multifile JSON; attempt to strip outer braces.
        if source_code.startswith("{") and source_code.endswith("}"):
            inner = source_code.strip().lstrip("{").rstrip("}")
            source_code = inner

        seen = set()
        for pattern, code, severity, description in PATTERNS:
            try:
                hits = list(re.finditer(pattern, source_code))
            except re.error:
                continue
            if hits and code not in seen:
                seen.add(code)
                findings.append({
                    "category": "source",
                    "code": code,
                    "severity": severity,
                    "description": description,
                    "occurrences": len(hits),
                })
        return findings
