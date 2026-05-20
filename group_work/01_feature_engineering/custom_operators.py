"""
Custom operators added for stage 1 feature engineering.

These operators are used by factor formulas translated from 实战因子365.
The same implementations should be copied into code/stock1800/feature.py
so factor functions can import them from the shared operator library.
"""

import numpy as np
import pandas as pd


def safe_div(x, y):
    """Element-wise safe division. Zero denominators are treated as NaN."""
    return x / y.replace(0, np.nan)


def SignedPower(x, power):
    """Signed power: sign(x) * abs(x) ** power."""
    return np.sign(x) * (np.abs(x) ** power)


def SignedSqrt(x):
    """Signed square root: sign(x) * sqrt(abs(x))."""
    return np.sign(x) * np.sqrt(np.abs(x))


def Log(x):
    """Natural log with non-positive values set to NaN."""
    return np.log(x.where(x > 0))


def Abs(x):
    """Element-wise absolute value."""
    return x.abs()


def Round(x):
    """Element-wise round."""
    return np.round(x)


def pn_Stand(df2):
    """Cross-sectional z-score standardization for each date."""
    mean = df2.mean(axis=1)
    std = df2.std(axis=1).replace(0, np.nan)
    return df2.sub(mean, axis=0).div(std, axis=0)


def ts_Rank(df2, window):
    """Time-series rolling percentile rank."""
    return df2.rolling(window).rank(pct=True)


def ts_ChgRate(df2, window):
    """Time-series percentage change over a fixed window."""
    return df2 / df2.shift(window) - 1


def ts_Corr(x, y, window):
    """Rolling time-series correlation between two aligned DataFrames."""
    return x.rolling(window).corr(y)


def ts_WMA(df2, window):
    """Linearly weighted moving average. Latest observation has largest weight."""
    weights = np.arange(1, window + 1, dtype=float)
    weights = weights / weights.sum()
    return df2.rolling(window).apply(lambda arr: np.dot(arr, weights), raw=True)


def ts_EMA(df2, span):
    """Exponential moving average."""
    return df2.ewm(span=span, adjust=False).mean()


def ts_IR(df2, window):
    """Rolling information ratio: rolling mean / rolling std."""
    mean = df2.rolling(window).mean()
    std = df2.rolling(window).std().replace(0, np.nan)
    return mean / std


def ts_MaxDrawdownAbs(df2, window):
    """
    Rolling drawdown-like measure for fund-flow series.

    This version is more robust for fund-flow data that may be negative.
    """
    def _mdd(arr):
        s = pd.Series(arr)
        peak = s.cummax()
        scale = peak.abs().replace(0, np.nan)
        dd = (peak - s) / scale
        return dd.max()

    return df2.rolling(window).apply(_mdd, raw=True)


__all__ = [
    "safe_div",
    "SignedPower",
    "SignedSqrt",
    "Log",
    "Abs",
    "Round",
    "pn_Stand",
    "ts_Rank",
    "ts_ChgRate",
    "ts_Corr",
    "ts_WMA",
    "ts_EMA",
    "ts_IR",
    "ts_MaxDrawdownAbs",
]