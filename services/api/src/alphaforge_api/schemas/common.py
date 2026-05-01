from __future__ import annotations

from typing import Generic, Sequence, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PageMeta(BaseModel):
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool


class Page(BaseModel, Generic[T]):
    items: Sequence[T] = Field(default_factory=list)
    meta: PageMeta


class HealthOut(BaseModel):
    ok: bool
    detail: str | None = None
