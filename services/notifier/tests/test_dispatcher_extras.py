from __future__ import annotations

import asyncio
from typing import Any

import pytest
from alphaforge_notifier.channels.base import Channel, DeliveryResult
from alphaforge_notifier.dispatcher import NotifierDispatcher


class _RecordingChannel(Channel):
    name = "test"

    def __init__(self, *, fail: bool = False) -> None:
        self.calls: list[dict[str, Any]] = []
        self.fail = fail

    async def send(self, alert: dict[str, Any], rendered: dict[str, str]) -> DeliveryResult:
        self.calls.append({"alert": alert, "rendered": rendered})
        if self.fail:
            raise RuntimeError("boom")
        return DeliveryResult(channel="test", success=True)


def _run(coro):
    return asyncio.new_event_loop().run_until_complete(coro)


@pytest.fixture
def dispatcher() -> NotifierDispatcher:
    d = NotifierDispatcher()
    return d


def _alert(alert_id: str = "a-1", channels: list[str] | None = None, owner: str = "u1") -> dict[str, Any]:
    return {
        "alert_id": alert_id,
        "rule_type": "anomaly",
        "symbol": "ETH/USDT",
        "owner_id": owner,
        "channels": channels or ["test"],
        "title": "Anomaly detected",
        "message": "abnormal volume",
        "severity": "high",
        "payload": {"digest": "x"},
    }


def test_dispatch_succeeds_via_recording_channel(
    dispatcher: NotifierDispatcher,
) -> None:
    ch = _RecordingChannel()
    dispatcher._channels = {"test": ch}
    results = _run(dispatcher.dispatch(_alert()))
    assert len(results) == 1
    assert results[0].success
    assert ch.calls and ch.calls[0]["alert"]["alert_id"] == "a-1"


def test_dispatch_unknown_channel_returns_error(dispatcher: NotifierDispatcher) -> None:
    dispatcher._channels = {}
    results = _run(dispatcher.dispatch(_alert(channels=["nope"])))
    assert results[0].success is False
    assert results[0].error == "unknown_channel"


def test_dispatch_dedup_blocks_second_identical_alert(
    dispatcher: NotifierDispatcher,
) -> None:
    ch = _RecordingChannel()
    dispatcher._channels = {"test": ch}
    a = _alert(alert_id="dup-1")
    _run(dispatcher.dispatch(a))
    second = _run(dispatcher.dispatch(a))
    assert second[0].channel == "dedup" and second[0].success is False


def test_dispatch_propagates_send_exception_as_error_result(
    dispatcher: NotifierDispatcher,
) -> None:
    ch = _RecordingChannel(fail=True)
    dispatcher._channels = {"test": ch}
    results = _run(dispatcher.dispatch(_alert()))
    assert results[0].success is False
    assert "boom" in (results[0].error or "")
