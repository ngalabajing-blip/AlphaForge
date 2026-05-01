from decimal import Decimal

import pytest
from alphaforge_shared.events import (
    AnomalyEvent,
    BlockEvent,
    EventSeverity,
    PriceEvent,
    SignalAction,
    SignalEvent,
    TransactionEvent,
)


def test_block_event_roundtrip():
    e = BlockEvent(
        producer="ingestor",
        chain="eth",
        height=20_000_000,
        block_hash="0xabc",
        parent_hash="0xdef",
        tx_count=120,
    )
    payload = e.model_dump_json()
    parsed = BlockEvent.model_validate_json(payload)
    assert parsed.height == e.height
    assert parsed.schema == "af.chain.block.v1"


def test_transaction_event_decimal_coercion():
    e = TransactionEvent(
        producer="ingestor",
        chain="eth",
        block_height=1,
        tx_hash="0x1",
        sender="0xS",
        recipient="0xR",
        value_native="1.234567",
    )
    assert e.value_native == Decimal("1.234567")


def test_price_event_required_fields():
    PriceEvent(
        producer="ingestor",
        source="coingecko",
        chain="eth",
        symbol="ETH",
        address=None,
        price_usd=Decimal("3000"),
    )


def test_signal_event_action_enum():
    s = SignalEvent(
        producer="worker",
        strategy_id="s1",
        run_id="r1",
        symbol="ETH/USDC",
        action="buy",
        strength=0.8,
    )
    assert s.action is SignalAction.BUY


def test_anomaly_severity_enum():
    a = AnomalyEvent(
        producer="ml",
        chain="eth",
        subject_type="address",
        subject="0x1",
        score=0.92,
        threshold=0.7,
        label="anomalous",
        severity=EventSeverity.HIGH,
        explanation="outlier feature combination",
    )
    assert a.severity is EventSeverity.HIGH


def test_event_envelope_immutable():
    e = BlockEvent(
        producer="ingestor",
        chain="eth",
        height=1,
        block_hash="0xa",
        parent_hash="0xb",
        tx_count=0,
    )
    with pytest.raises(Exception):
        e.height = 2  # type: ignore[misc]
