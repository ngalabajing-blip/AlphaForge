"""
Canonical token / market symbol parsing and registry helpers.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass

_SYMBOL_RE = re.compile(r"^([A-Z0-9]{1,12})/([A-Z0-9]{1,12})$")


@dataclass(frozen=True)
class MarketSymbol:
    base: str
    quote: str

    @property
    def canonical(self) -> str:
        return f"{self.base}/{self.quote}"

    def inverted(self) -> MarketSymbol:
        return MarketSymbol(self.quote, self.base)


def parse_symbol(text: str) -> MarketSymbol:
    """Parse a market symbol of the form ``BASE/QUOTE``.

    Examples
    --------
    >>> parse_symbol("ETH/USDC").canonical
    'ETH/USDC'
    """
    text = text.strip().upper()
    m = _SYMBOL_RE.match(text)
    if not m:
        raise ValueError(f"invalid market symbol: {text!r}")
    return MarketSymbol(m.group(1), m.group(2))


# Common stable / quote tokens used to score symbol popularity.
STABLES: tuple[str, ...] = (
    "USDT",
    "USDC",
    "DAI",
    "BUSD",
    "FRAX",
    "USD",
    "TUSD",
    "PYUSD",
)
MAJORS: tuple[str, ...] = (
    "BTC",
    "ETH",
    "SOL",
    "BNB",
    "MATIC",
    "AVAX",
    "OP",
    "ARB",
    "ATOM",
)


def is_stable(symbol: str) -> bool:
    return symbol.upper() in STABLES


def is_major(symbol: str) -> bool:
    return symbol.upper() in MAJORS


def rank_symbol(sym: MarketSymbol) -> int:
    """Heuristic ranking — lower is more "interesting" (used to break ties)."""
    score = 0
    if not is_stable(sym.quote):
        score += 5
    if is_major(sym.base):
        score -= 2
    return score


def normalise_pair(left: str, right: str) -> MarketSymbol:
    """Choose a canonical ordering for an unordered token pair."""
    a, b = left.upper(), right.upper()
    if is_stable(a) and not is_stable(b):
        return MarketSymbol(b, a)
    if is_stable(b):
        return MarketSymbol(a, b)
    return MarketSymbol(*sorted([a, b]))


def all_symbols_with(quote: str, bases: Iterable[str]) -> list[MarketSymbol]:
    return [MarketSymbol(b.upper(), quote.upper()) for b in bases]
