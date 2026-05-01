from __future__ import annotations

import asyncio
from typing import Any

import pytest

from alphaforge_notifier.dispatcher import NotificationDispatcher
from alphaforge_notifier.channels import Channel


class _RecordingChannel(Channel):
    def __init__(self, name: str, *, fail_on: int | None = None) -> None:
        self.name = name
        self.calls: list[dict[str, Any]] = []
        self.fail_on = fail_on
        self.invocation = 0

    async def send(self, payload: dict[str, Any]) -> dict[str, Any]:
        self.invocation += 1
        self.calls.append(payload)
        if self.fail_on is not None and self.invocation == self.fail_on:
            raise RuntimeError("boom")
        return {"channel": self.name, "ok": True}


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


def test_dispatcher_fans_out_to_all_channels() -> None:
    a = _RecordingChannel("telegram")
    b = _RecordingChannel("discord")
    disp = NotificationDispatcher(channels={"telegram": a, "discord": b})
    out = _run(disp.dispatch({"channels": ["telegram", "discord"], "payload": {"x": 1}}))
    assert {r["channel"] for r in out} == {"telegram", "discord"}
    assert a.calls == [{"x": 1}]
    assert b.calls == [{"x": 1}]


def test_dispatcher_skips_unknown_channel() -> None:
    a = _RecordingChannel("telegram")
    disp = NotificationDispatcher(channels={"telegram": a})
    out = _run(disp.dispatch({"channels": ["telegram", "nope"], "payload": {"x": 2}}))
    names = {r["channel"] for r in out}
    assert "telegram" in names
    assert "nope" not in names


def test_dispatcher_records_failure() -> None:
    a = _RecordingChannel("telegram", fail_on=1)
    disp = NotificationDispatcher(channels={"telegram": a})
    out = _run(disp.dispatch({"channels": ["telegram"], "payload": {"x": 3}}))
    assert out[0]["channel"] == "telegram"
    assert out[0]["ok"] is False
    assert "boom" in out[0]["error"]
