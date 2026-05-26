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


def Sin(x):
    """Element-wise sine."""
    return np.sin(x)


def pn_Stand(df2):
    """Cross-sectional z-score standardization for each date."""
    mean = df2.mean(axis=1)
    std = df2.std(axis=1).replace(0, np.nan)
    return df2.sub(mean, axis=0).div(std, axis=0)


def pn_CSPct(df2, q):
    """Cross-sectional top-quantile indicator for each date."""
    threshold = df2.quantile(q, axis=1)
    return df2.ge(threshold, axis=0).astype(float)


def pn_CSSkew(df2):
    """Cross-sectional skewness replicated across columns for each date."""
    skew = df2.skew(axis=1)
    return pd.DataFrame(
        np.repeat(skew.values[:, None], len(df2.columns), axis=1),
        index=df2.index,
        columns=df2.columns,
    )


def pn_GroupRank(df2, group):
    """Cross-sectional percentile rank within each date/group bucket."""
    out = pd.DataFrame(np.nan, index=df2.index, columns=df2.columns)
    group_aligned = group.reindex(index=df2.index, columns=df2.columns)
    for idx in df2.index:
        values = df2.loc[idx]
        groups = group_aligned.loc[idx]
        for _, cols in groups.dropna().groupby(groups.dropna()).groups.items():
            out.loc[idx, cols] = values.loc[cols].rank(pct=True)
    return out


def pn_GroupStdev(df2, group):
    """Cross-sectional group standard deviation replicated to group members."""
    out = pd.DataFrame(np.nan, index=df2.index, columns=df2.columns)
    group_aligned = group.reindex(index=df2.index, columns=df2.columns)
    for idx in df2.index:
        values = df2.loc[idx]
        groups = group_aligned.loc[idx]
        for _, cols in groups.dropna().groupby(groups.dropna()).groups.items():
            out.loc[idx, cols] = values.loc[cols].std()
    return out


def Winsorize(df2, method=1):
    """Cross-sectional winsorization; method 1 uses median +/- 5.2 MAD."""
    if method != 1:
        mean = df2.mean(axis=1)
        std = df2.std(axis=1).replace(0, np.nan)
        lower = mean - 3 * std
        upper = mean + 3 * std
    else:
        median = df2.median(axis=1)
        mad = df2.sub(median, axis=0).abs().median(axis=1).replace(0, np.nan)
        lower = median - 5.2 * mad
        upper = median + 5.2 * mad
    return df2.clip(lower=lower, upper=upper, axis=0)


def ts_Rank(df2, window):
    """Time-series rolling percentile rank."""
    return df2.rolling(window).rank(pct=True)


def ts_ChgRate(df2, window):
    """Time-series percentage change over a fixed window."""
    return df2 / df2.shift(window) - 1


def ts_Corr(x, y, window):
    """Rolling time-series correlation between two aligned DataFrames."""
    return x.rolling(window).corr(y)


def ts_TopKSum(df2, window, k):
    """Rolling sum of the largest k observations in each window."""
    k = int(k)

    def _topk_sum(arr):
        arr = arr[~np.isnan(arr)]
        if len(arr) == 0:
            return np.nan
        kk = min(k, len(arr))
        return np.sort(arr)[-kk:].sum()

    return df2.rolling(window).apply(_topk_sum, raw=True)


def ts_MaxMean(df2, window, mean_window):
    """Rolling max of a shorter rolling mean."""
    return df2.rolling(mean_window).mean().rolling(window).max()


def ts_MaxStd(df2, window, std_window):
    """Rolling max of a shorter rolling standard deviation."""
    return df2.rolling(std_window).std().rolling(window).max()


def ts_MinDiff(df2, window):
    """Latest value minus rolling minimum."""
    return df2 - df2.rolling(window).min()


def ts_AvDiff(df2, window):
    """Latest value minus rolling mean."""
    return df2 - df2.rolling(window).mean()


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
    "Sin",
    "pn_Stand",
    "pn_CSPct",
    "pn_CSSkew",
    "pn_GroupRank",
    "pn_GroupStdev",
    "Winsorize",
    "ts_Rank",
    "ts_ChgRate",
    "ts_Corr",
    "ts_TopKSum",
    "ts_MaxMean",
    "ts_MaxStd",
    "ts_MinDiff",
    "ts_AvDiff",
    "ts_WMA",
    "ts_EMA",
    "ts_IR",
    "ts_MaxDrawdownAbs",
]
