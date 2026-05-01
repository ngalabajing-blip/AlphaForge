from alphaforge_auditor.scanners.source_scanner import SourceScanner


def test_selfdestruct_in_source():
    src = "function kill() public { selfdestruct(payable(owner)); }"
    findings = SourceScanner().analyse(src)
    codes = [f["code"] for f in findings]
    assert "SOL_SELFDESTRUCT" in codes


def test_blacklist_detected():
    src = "function blacklist(address user) external onlyOwner {}"
    findings = SourceScanner().analyse(src)
    codes = [f["code"] for f in findings]
    assert "SOL_BLACKLIST" in codes
    assert "SOL_ONLY_OWNER" in codes


def test_no_findings_on_clean_code():
    src = "function totalSupply() external view returns (uint256) { return _totalSupply; }"
    findings = SourceScanner().analyse(src)
    assert findings == []


def test_empty_source():
    assert SourceScanner().analyse("") == []
