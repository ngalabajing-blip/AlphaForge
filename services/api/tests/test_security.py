import time

import pytest
from jose import jwt

from alphaforge_api.core.config import get_settings
from alphaforge_api.core.security import (
    Role,
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_api_key,
    hash_api_key,
    hash_password,
    verify_password,
)


def test_password_hash_roundtrip():
    h = hash_password("hunter2-very-long")
    assert verify_password("hunter2-very-long", h)
    assert not verify_password("wrong", h)


def test_jwt_roundtrip():
    token = create_access_token(subject="user-1", role=Role.RESEARCHER)
    payload = decode_token(token)
    assert payload["sub"] == "user-1"
    assert payload["role"] == "researcher"
    assert payload["type"] == "access"


def test_jwt_expiry():
    s = get_settings()
    token = create_access_token(subject="user-1", role=Role.VIEWER)
    payload = jwt.decode(token, s.jwt_secret_key, algorithms=[s.jwt_algorithm])
    assert payload["exp"] > int(time.time())


def test_refresh_token_type():
    refresh = create_refresh_token(subject="u")
    payload = decode_token(refresh)
    assert payload["type"] == "refresh"


def test_api_key_hash_unique():
    p1, h1 = generate_api_key()
    p2, h2 = generate_api_key()
    assert p1 != p2 and h1 != h2
    assert hash_api_key(p1) == h1
