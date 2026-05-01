from decimal import Decimal

from alphaforge_ingestor.pipeline.normaliser import (
    hex_to_int,
    lamports_to_sol,
    wei_to_eth,
)


def test_wei_to_eth_int():
    assert wei_to_eth(10**18) == Decimal("1")


def test_wei_to_eth_hex():
    assert wei_to_eth("0x" + hex(10**18)[2:]) == Decimal("1")


def test_lamports_to_sol():
    assert lamports_to_sol(10**9) == Decimal("1")


def test_hex_to_int():
    assert hex_to_int("0x10") == 16
    assert hex_to_int(42) == 42
    assert hex_to_int("100") == 100
