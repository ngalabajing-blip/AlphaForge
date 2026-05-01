"""Tiny, dependency-free helpers used across services."""
from __future__ import annotations

import asyncio
import functools
import hashlib
import math
import re
import time
import uuid
from contextlib import contextmanager
from decimal import Decimal, InvalidOperation
from typing import Any, Awaitable, Callable, Iterable, Iterator, TypeVar

T = TypeVar("T")
R = TypeVar("R")


def new_uuid() -> str:
    return uuid.uuid4().hex


def utc_now_ms() -> int:
    return int(time.time() * 1000)


def to_decimal(value: Any, *, default: Decimal | None = Decimal("0")) -> Decimal:
    """Best-effort coerce to :class:`Decimal`. Returns ``default`` on failure."""
    if isinstance(value, Decimal):
        return value
    if value is None:
        if default is None:
            raise ValueError("None cannot be converted to Decimal")
        return default
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        if default is None:
            raise
        return default


def safe_div(num: Decimal, den: Decimal, *, default: Decimal = Decimal("0")) -> Decimal:
    if den == 0:
        return default
    return num / den


def chunked(seq: Iterable[T], size: int) -> Iterator[list[T]]:
    if size <= 0:
        raise ValueError("size must be > 0")
    buf: list[T] = []
    for item in seq:
        buf.append(item)
        if len(buf) == size:
            yield buf
            buf = []
    if buf:
        yield buf


def normalise_address(addr: str) -> str:
    """Normalise an EVM-style address: lowercase, ensure 0x prefix."""
    if addr is None:
        raise ValueError("address is None")
    addr = addr.strip()
    if not addr:
        raise ValueError("address is empty")
    if not addr.startswith("0x"):
        addr = "0x" + addr
    if not re.fullmatch(r"0x[0-9a-fA-F]{40}", addr):
        raise ValueError(f"not an EVM address: {addr!r}")
    return addr.lower()


def short_addr(addr: str, head: int = 6, tail: int = 4) -> str:
    """Display-friendly truncation: 0xabcd…1234."""
    addr = addr or ""
    if len(addr) <= head + tail:
        return addr
    return f"{addr[:head]}…{addr[-tail:]}"


def keccak_id(value: str) -> str:
    """Stable string id derived from value (sha256 trim — no extra deps)."""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


@contextmanager
def stopwatch() -> Iterator[Callable[[], float]]:
    """Context manager yielding a callable returning the elapsed seconds."""
    start = time.perf_counter()
    yield lambda: time.perf_counter() - start


def retry_async(
    *,
    attempts: int = 3,
    backoff_seconds: float = 0.5,
    backoff_factor: float = 2.0,
    exceptions: tuple[type[BaseException], ...] = (Exception,),
) -> Callable[[Callable[..., Awaitable[R]]], Callable[..., Awaitable[R]]]:
    """Decorator: retry an async callable with exponential backoff."""

    def decorator(fn: Callable[..., Awaitable[R]]) -> Callable[..., Awaitable[R]]:
        @functools.wraps(fn)
        async def wrapper(*args: Any, **kwargs: Any) -> R:
            delay = backoff_seconds
            last: BaseException | None = None
            for attempt in range(1, attempts + 1):
                try:
                    return await fn(*args, **kwargs)
                except exceptions as exc:
                    last = exc
                    if attempt == attempts:
                        break
                    await asyncio.sleep(delay)
                    delay *= backoff_factor
            assert last is not None
            raise last

        return wrapper

    return decorator


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def percentile(values: list[float], q: float) -> float:
    """Linear-interpolation percentile (q in 0..100)."""
    if not values:
        return 0.0
    if not 0 <= q <= 100:
        raise ValueError("q must be 0..100")
    s = sorted(values)
    if q == 0:
        return s[0]
    if q == 100:
        return s[-1]
    rank = (q / 100) * (len(s) - 1)
    lo_idx = math.floor(rank)
    hi_idx = math.ceil(rank)
    if lo_idx == hi_idx:
        return s[lo_idx]
    frac = rank - lo_idx
    return s[lo_idx] * (1 - frac) + s[hi_idx] * frac


def humanize_amount(value: Decimal, *, decimals: int = 2) -> str:
    """Render a Decimal with thousands separators."""
    if value is None:
        return "—"
    quant = Decimal(10) ** -decimals
    rounded = value.quantize(quant)
    return f"{rounded:,}"
