"""Technical indicators registry."""
from alphaforge_worker.indicators.registry import INDICATORS, Indicator, register_indicator
from alphaforge_worker.indicators.basic import EMA, SMA, RSI, MACD, ATR, Bollinger, Stochastic, ADX
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

__all__ = [
    "INDICATORS",
    "Indicator",
    "register_indicator",
    "EMA", "SMA", "RSI", "MACD", "ATR", "Bollinger", "Stochastic", "ADX",
    "OBV", "VWAP", "Aroon", "ChaikinMoneyFlow", "Donchian", "Ichimoku",
    "KeltnerChannels", "Supertrend",
]
