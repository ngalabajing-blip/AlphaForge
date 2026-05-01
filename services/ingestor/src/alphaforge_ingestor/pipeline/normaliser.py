"""
Normalise raw chain payloads into the canonical event schema.

Currently the EVM adapter performs the conversion inline; this module exists
so that future contributors have a single place to host normalisation
helpers without poking at adapter internals.
"""

from __future__ import annotations

from decimal import Decimal


def wei_to_eth(wei: int | str) -> Decimal:
    if isinstance(wei, str):
        wei = int(wei, 16) if wei.startswith("0x") else int(wei)
    return Decimal(wei) / Decimal(10**18)


def lamports_to_sol(lamports: int) -> Decimal:
    return Decimal(lamports) / Decimal(10**9)


def hex_to_int(value: str | int) -> int:
    if isinstance(value, int):
        return value
    return int(value, 16) if value.startswith("0x") else int(value)
