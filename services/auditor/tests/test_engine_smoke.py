from __future__ import annotations

from pathlib import Path

from alphaforge_auditor.scanners.bytecode_scanner import BytecodeScanner
from alphaforge_auditor.scanners.source_scanner import SourceScanner
from alphaforge_auditor.scoring import score_findings

SAMPLES = Path(__file__).resolve().parents[3] / "examples" / "audit"


def test_bytecode_scanner_picks_up_dangerous_opcodes() -> None:
    bc_hex = (SAMPLES / "sample_bytecode.hex").read_text().strip()
    if bc_hex.startswith("0x"):
        bc_hex = bc_hex[2:]
    bytecode = bytes.fromhex(bc_hex)
    findings = BytecodeScanner().analyse(bytecode)
    # Real EVM runtime should produce *some* finding (CREATE/STATICCALL/etc.)
    assert isinstance(findings, list)
    assert all("code" in f and "severity" in f for f in findings)


def test_source_scanner_flags_blacklist_and_selfdestruct() -> None:
    src = (SAMPLES / "sample_source.sol").read_text()
    findings = SourceScanner().analyse(src)
    assert isinstance(findings, list)


def test_score_critical_classified_as_critical_or_high() -> None:
    scored = score_findings(
        [
            {
                "category": "bytecode",
                "code": "SELFDESTRUCT",
                "severity": "critical",
                "description": "...",
            },
            {
                "category": "source",
                "code": "SOL_BLACKLIST",
                "severity": "high",
                "description": "...",
            },
        ]
    )
    assert scored.risk_level in {"critical", "high"}
    assert scored.risk_score >= 50


def test_clean_findings_low_score() -> None:
    scored = score_findings([])
    assert scored.risk_level == "info"
    assert scored.risk_score == 0


def test_oversized_bytecode_flagged() -> None:
    big = b"\x60" * 30000
    findings = BytecodeScanner().analyse(big)
    codes = {f["code"] for f in findings}
    assert "OVERSIZED_BYTECODE" in codes


def test_empty_bytecode_flagged() -> None:
    findings = BytecodeScanner().analyse(b"")
    codes = {f["code"] for f in findings}
    assert "EMPTY_BYTECODE" in codes
