"""Technical indicators registry."""

from alphaforge_worker.indicators.advanced import (
    OBV,
    VWAP,
    Aroon,
    ChaikinMoneyFlow,
    Donchian,
    Ichimoku,
    KeltnerChannels,
    Supertrend,
)
from alphaforge_worker.indicators.basic import (
    ADX,
    ATR,
    EMA,
    MACD,
    RSI,
    SMA,
    Bollinger,
    Stochastic,
)
from alphaforge_worker.indicators.registry import (
    INDICATORS,
    Indicator,
    register_indicator,
)

__all__ = [
    "INDICATORS",
    "Indicator",
    "register_indicator",
    "EMA",
    "SMA",
    "RSI",
    "MACD",
    "ATR",
    "Bollinger",
    "Stochastic",
    "ADX",
    "OBV",
    "VWAP",
    "Aroon",
    "ChaikinMoneyFlow",
    "Donchian",
    "Ichimoku",
    "KeltnerChannels",
    "Supertrend",
]
