from alphaforge_ml.models.sentiment import LexiconSentiment


def test_positive():
    s = LexiconSentiment().predict("ETH is mooning, super bullish breakout")
    assert s.label == "positive"
    assert s.score > 0


def test_negative():
    s = LexiconSentiment().predict("Massive dump, looks like a rug pull")
    assert s.label == "negative"
    assert s.score < 0


def test_neutral():
    s = LexiconSentiment().predict("good morning frens, beautiful weather today")
    assert s.label == "neutral"


def test_negation_inverts():
    pos = LexiconSentiment().predict("rally pump")
    neg = LexiconSentiment().predict("not pump never rally")
    assert pos.score > 0
    assert neg.score <= pos.score


def test_empty():
    s = LexiconSentiment().predict("")
    assert s.score == 0.0
