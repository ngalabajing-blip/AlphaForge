from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class AuditRequestIn(BaseModel):
    chain: str = Field(min_length=2, max_length=32)
    address: str = Field(min_length=4, max_length=64)
    deep: bool = True


class FindingOut(BaseModel):
    rule: str
    severity: str
    title: str
    description: str
    location: Optional[str]
    cwe: Optional[str]
    swc: Optional[str]


class AuditOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    chain: str
    address: str
    status: str
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    risk_score: Optional[float]
    risk_level: Optional[str]
    summary: Optional[str]
    findings: list[dict[str, Any]] = Field(default_factory=list)
    bytecode_size: Optional[int]
    has_source: Optional[bool]
    error: Optional[str]
    created_at: datetime
