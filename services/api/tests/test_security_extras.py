from __future__ import annotations

import time

import pytest

from alphaforge_api.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_api_key,
    verify_api_key,
)


def test_access_and_refresh_tokens_are_distinct() -> None:
    a = create_access_token(subject="user-1", scopes=["read"])
    r = create_refresh_token(subject="user-1")
    assert a != r
    decoded_a = decode_token(a)
    decoded_r = decode_token(r)
    assert decoded_a["sub"] == decoded_r["sub"] == "user-1"
    assert decoded_a["type"] == "access"
    assert decoded_r["type"] == "refresh"


def test_decode_invalid_token_raises() -> None:
    with pytest.raises(Exception):
        decode_token("not-a-token")


def test_api_key_hash_roundtrip() -> None:
    raw = "afk_" + "a" * 32
    digest = hash_api_key(raw)
    assert digest != raw
    assert verify_api_key(raw, digest)
    assert not verify_api_key(raw + "b", digest)


def test_access_token_includes_scopes() -> None:
    token = create_access_token(subject="user-2", scopes=["read", "write"])
    decoded = decode_token(token)
    assert "read" in decoded["scope"]
    assert "write" in decoded["scope"]


@pytest.mark.skipif(time is None, reason="time not available")
def test_token_has_exp_in_future() -> None:
    token = create_access_token(subject="u", scopes=[])
    decoded = decode_token(token)
    assert decoded["exp"] > int(time.time())
