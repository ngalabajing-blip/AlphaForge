from alphaforge_ingestor.pipeline.decoder import EVENT_SIGNATURES, EVMLogDecoder


def test_decode_transfer():
    decoder = EVMLogDecoder()
    log_entry = {
        "topics": [
            "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
            "0x000000000000000000000000aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "0x000000000000000000000000bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        ],
        "data": "0x00",
    }
    name, args = decoder.try_decode(log_entry)
    assert name == "Transfer"
    assert args["topic1"].startswith("0xaa")
    assert args["topic2"].startswith("0xbb")


def test_unknown_signature():
    decoder = EVMLogDecoder()
    name, args = decoder.try_decode({"topics": ["0x" + "0" * 64]})
    assert name is None
    assert args is None


def test_no_topics():
    assert EVMLogDecoder().try_decode({"topics": []}) == (None, None)


def test_signatures_table_size():
    assert len(EVENT_SIGNATURES) >= 5
