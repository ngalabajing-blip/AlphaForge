from alphaforge_auditor.scanners.bytecode_scanner import BytecodeScanner


def test_empty_bytecode_flagged():
    findings = BytecodeScanner().analyse(b"")
    codes = [f["code"] for f in findings]
    assert "EMPTY_BYTECODE" in codes


def test_selfdestruct_flagged():
    code = bytes.fromhex("60806040" + "ff0000" + "60ff")
    findings = BytecodeScanner().analyse(code)
    codes = [f["code"] for f in findings]
    assert "SELFDESTRUCT" in codes


def test_delegatecall_flagged():
    code = bytes.fromhex("60806040" + "f4" + "60ff")
    findings = BytecodeScanner().analyse(code)
    codes = [f["code"] for f in findings]
    assert "DELEGATECALL" in codes


def test_clean_bytecode_no_critical():
    code = bytes.fromhex("60806040" + "00" * 64)
    findings = BytecodeScanner().analyse(code)
    crits = [f for f in findings if f["severity"] == "critical"]
    assert crits == []
