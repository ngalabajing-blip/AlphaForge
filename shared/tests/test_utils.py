from decimal import Decimal

import pytest

from alphaforge_shared.utils import (
    chunked,
    clamp,
    humanize_amount,
    keccak_id,
    normalise_address,
    percentile,
    safe_div,
    short_addr,
    to_decimal,
)


def test_normalise_address_pads_prefix_and_lowercases():
    addr = normalise_address("0xABCDEF0123456789abcdef0123456789AbCdEf01")
    assert addr.startswith("0x") and addr == addr.lower()


def test_normalise_address_invalid_raises():
    with pytest.raises(ValueError):
        normalise_address("not-an-address")


def test_short_addr_truncates_only_when_long():
    assert short_addr("0x1234") == "0x1234"
    assert "…" in short_addr("0x" + "a" * 40)


def test_chunked_basic():
    assert list(chunked([1, 2, 3, 4, 5], 2)) == [[1, 2], [3, 4], [5]]


def test_to_decimal_default():
    assert to_decimal(None) == Decimal("0")
    assert to_decimal("1.5") == Decimal("1.5")


def test_safe_div_zero_default():
    assert safe_div(Decimal("1"), Decimal("0")) == Decimal("0")


def test_clamp_bounds():
    assert clamp(5, 0, 10) == 5
    assert clamp(-1, 0, 10) == 0
    assert clamp(99, 0, 10) == 10


def test_percentile_known_values():
    assert percentile([1, 2, 3, 4], 50) == 2.5
    assert percentile([], 50) == 0.0


def test_keccak_id_stable():
    assert keccak_id("foo") == keccak_id("foo")
    assert keccak_id("foo") != keccak_id("bar")


def test_humanize_amount_thousands():
    assert humanize_amount(Decimal("1234567.891")) == "1,234,567.89"
