"""Pydantic v2 schemas — request/response payloads."""

from alphaforge_api.schemas.alert import (
    AlertCreate,
    AlertDeliveryOut,
    AlertOut,
    AlertUpdate,
)
from alphaforge_api.schemas.audit import AuditOut, AuditRequestIn, FindingOut
from alphaforge_api.schemas.backtest import (
    BacktestCreate,
    BacktestOut,
    BacktestSummary,
    BacktestTradeOut,
)
from alphaforge_api.schemas.common import Page, PageMeta
from alphaforge_api.schemas.signal import SignalOut, SignalQuery
from alphaforge_api.schemas.strategy import (
    StrategyCreate,
    StrategyOut,
    StrategyUpdate,
    StrategyVersionOut,
)
from alphaforge_api.schemas.user import (
    APIKeyCreate,
    APIKeyCreated,
    APIKeyOut,
    TokenPair,
    UserCreate,
    UserLogin,
    UserOut,
)

__all__ = [
    "Page",
    "PageMeta",
    "UserCreate",
    "UserOut",
    "UserLogin",
    "TokenPair",
    "APIKeyCreate",
    "APIKeyOut",
    "APIKeyCreated",
    "StrategyCreate",
    "StrategyUpdate",
    "StrategyOut",
    "StrategyVersionOut",
    "BacktestCreate",
    "BacktestOut",
    "BacktestSummary",
    "BacktestTradeOut",
    "SignalOut",
    "SignalQuery",
    "AlertCreate",
    "AlertOut",
    "AlertUpdate",
    "AlertDeliveryOut",
    "AuditRequestIn",
    "AuditOut",
    "FindingOut",
]
