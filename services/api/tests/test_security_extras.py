from __future__ import annotations

import time

import pytest
from alphaforge_api.core.security import (
    Role,
    constant_time_eq,
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_api_key,
    hash_api_key,
    hash_password,
    verify_password,
)
from fastapi import HTTPException


def test_password_roundtrip() -> None:
    h = hash_password("s3cret")
    assert h != "s3cret"
    assert verify_password("s3cret", h)
    assert not verify_password("nope", h)


def test_access_and_refresh_tokens_are_distinct() -> None:
    a = create_access_token(subject="user-1", role=Role.RESEARCHER)
    r = create_refresh_token(subject="user-1")
    assert a != r
    da = decode_token(a)
    dr = decode_token(r)
    assert da["sub"] == dr["sub"] == "user-1"
    assert da["type"] == "access"
    assert dr["type"] == "refresh"
    assert da["role"] == "researcher"


def test_decode_invalid_token_raises_401() -> None:
    with pytest.raises(HTTPException) as exc:
        decode_token("not-a-token")
    assert exc.value.status_code == 401


def test_api_key_hash_is_deterministic_and_unique() -> None:
    plain, h = generate_api_key()
    assert plain.startswith("afk_")
    assert hash_api_key(plain) == h
    assert hash_api_key(plain + "x") != h


def test_constant_time_eq_matches_for_equal_strings() -> None:
    assert constant_time_eq("abc", "abc")
    assert not constant_time_eq("abc", "abd")


def test_token_has_exp_in_future() -> None:
    token = create_access_token(subject="u", role=Role.VIEWER)
    decoded = decode_token(token)
    assert decoded["exp"] > int(time.time())


def test_admin_role_has_more_perms_than_viewer() -> None:
    from alphaforge_api.core.security import PERMISSIONS

    assert PERMISSIONS[Role.ADMIN] > PERMISSIONS[Role.VIEWER]
    assert "read:any" in PERMISSIONS[Role.VIEWER]
