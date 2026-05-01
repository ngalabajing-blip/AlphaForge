from alphaforge_auditor.scoring import score_findings


def test_critical_pushes_to_critical_level():
    res = score_findings([{"severity": "critical"}, {"severity": "high"}])
    assert res.risk_level in {"critical", "high"}
    assert res.risk_score >= 50


def test_no_findings_info():
    res = score_findings([])
    assert res.risk_level == "info"
    assert res.risk_score == 0
    assert "No notable" in res.summary


def test_score_capped_at_100():
    res = score_findings([{"severity": "critical"}] * 10)
    assert res.risk_score == 100
