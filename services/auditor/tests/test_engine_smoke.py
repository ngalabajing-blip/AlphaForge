from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from alphaforge_auditor.engine import AuditEngine
from alphaforge_auditor.scanners.bytecode_scanner import scan_bytecode
from alphaforge_auditor.scanners.source_scanner import scan_source
from alphaforge_auditor.scoring import score_findings


SAMPLES = Path(__file__).resolve().parents[3] / "examples" / "audit"


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


def test_bytecode_scanner_picks_up_selfdestruct() -> None:
    bc = (SAMPLES / "sample_bytecode.hex").read_text().strip()
    findings = scan_bytecode(bc)
    codes = {f["code"] for f in findings}
    assert "SELFDESTRUCT" in codes or "DELEGATECALL" in codes


def test_source_scanner_flags_blacklist_and_delegatecall() -> None:
    src = (SAMPLES / "sample_source.sol").read_text()
    findings = scan_source(src)
    codes = {f["code"] for f in findings}
    assert "SOL_BLACKLIST" in codes
    assert "SOL_DELEGATECALL" in codes
    assert "SOL_TX_ORIGIN" in codes


def test_clean_token_low_severity() -> None:
    src = (SAMPLES / "clean_token_source.sol").read_text()
    findings = scan_source(src)
    score = score_findings(findings)
    assert score["risk_level"] in ("info", "low")


def test_engine_orchestration_synthetic() -> None:
    engine = AuditEngine()
    bc = (SAMPLES / "sample_bytecode.hex").read_text().strip()
    src = (SAMPLES / "sample_source.sol").read_text()
    report = engine.synthesise_report(bytecode=bc, source=src)
    assert report["risk_level"] in ("medium", "high", "critical")
    assert report["risk_score"] > 0
    assert report["findings"]
