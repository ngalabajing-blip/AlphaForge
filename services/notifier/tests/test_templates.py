from alphaforge_notifier.templates import render_template


def test_render_minimal():
    out = render_template({"title": "hi", "symbol": "BTC", "severity": "info", "message": "msg"})
    assert "hi" in out["text"]
    assert "BTC" in out["text"]
    assert out["severity"] == "info"


def test_render_details():
    out = render_template(
        {
            "title": "t",
            "payload": {"price": 123, "delta": "+5%"},
        }
    )
    assert "price" in out["text"]
    assert "delta" in out["text"]
