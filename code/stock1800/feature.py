
import pandas as pd
import numpy as np

#%% get data

import math
import scipy.stats as st
##  PN

def Repmat(f_,lowBan):
    a = np.array([lowBan.values]).T
    c = np.tile(a,len(f_.columns))
    try:
        z = pd.DataFrame(c, index = f_.index, columns = f_.columns)
    except:
        c = np.reshape(c,(np.shape(c)[1],np.shape(c)[2]))
        z = pd.DataFrame(c, index = f_.index, columns = f_.columns)
    return z

def pn_TransNorm(s1):  # panel normalization
    from scipy.stats import norm
    dfCleaned = s1.copy()
    rank_ = dfCleaned.rank(pct=True, axis=1)
    cut = rank_.min(axis=1) / 2
    rank_ = rank_.sub(cut, axis=0)
    out = pd.DataFrame(norm.ppf(np.array(rank_)), index=rank_.index, columns=rank_.columns)
    return out


def pn_Rank(df2):
    """Cross-sectional percentile rank for each trade date."""
    df = df2.copy()
    return df.rank(pct=True, axis=1)


def pn_CrossResidual(y2, x2):
    """Daily cross-sectional residual of y on x with an intercept."""
    y = y2.copy()
    x = x2.copy()
    out = pd.DataFrame(np.nan, index=y.index, columns=y.columns)
    for idx in y.index:
        yy = y.loc[idx]
        xx = x.loc[idx]
        valid = yy.notna() & xx.notna()
        if valid.sum() < 3:
            continue
        x_valid = xx[valid].astype(float)
        y_valid = yy[valid].astype(float)
        x_var = x_valid.var()
        if pd.isna(x_var) or x_var == 0:
            out.loc[idx, valid] = y_valid - y_valid.mean()
            continue
        beta = x_valid.cov(y_valid) / x_var
        alpha = y_valid.mean() - beta * x_valid.mean()
        out.loc[idx, valid] = y_valid - (alpha + beta * x_valid)
    return out


def get_portFromFactor_both(f, num):
    f_ = f.copy()
    f_2 = f_.rank(axis=1,ascending=False,method = 'first')
    hold = f_.fillna(0) * 0
    hold[f_2 <= num] = 1
    hold = hold / Repmat(hold,hold.sum(1))
    hold2 = f_.fillna(0) * 0
    hold2[f_2 > Repmat(f_2,f_2.max(1)) - num] = 1
    hold2 = hold2 / Repmat(hold2,hold2.sum(1)) *-1
    return hold,hold2


def get_ls_post(f_D2):
    z_up = f_D2.copy()
    z_dn = f_D2.copy()
    z_up[z_up < 0] = 0
    z_dn[z_dn > 0] = 0
    z_up = z_up.div(z_up.sum(1), axis=0)
    z_dn = z_dn.div(z_dn.sum(1), axis=0) * -1
    return z_up.fillna(0), z_dn.fillna(0)


# calculator3
## TS
def ts_Delay(df2, num ):
    df = df2.copy()
    df3 = df.shift(num)   # shift, like:  df.shift(1), let yesterday's data to today 
    return df3   
 
def ts_Mean(df2, num):                # equal weight
    df = df2.copy()
    df = df.rolling(window=num).mean()
    return df



def ts_Decay(dataTD, nPrds):
    nPrds = int(nPrds)
    if nPrds > 0:
        w = np.array([1-1/nPrds*(i-1) for i in range(nPrds,0,-1)])
        w = w / sum(w)
        transformedTD = dataTD*w[-1]
        for i in range(nPrds-1):
            transformedTD = transformedTD+np.roll(dataTD,shift=nPrds-i-1,axis=0)*w[i]
        transformedTD[:nPrds] = np.nan
        return transformedTD
    else:
        return dataTD
    

def ts_DecayExp(dataTD2, nPrds):  # decayed weight: nonlinear change
    dataTD = dataTD2.copy()
    nPrds = int(nPrds)
    if nPrds > 0:
        alpha =1 - 2/(nPrds+1)
        w = np.array([alpha**i for i in range(nPrds,0,-1)])
        w = w / sum(w)
        transformedTD = dataTD*w[-1]
        for i in range(nPrds-1):
            transformedTD = transformedTD+np.roll(dataTD,shift=nPrds-i-1,axis=0)*w[i]
        transformedTD[:nPrds] = np.nan
        return transformedTD
    else:
        return dataTD
    
          
def ts_Max(df2, num):                # get the max value of last num trading day
    df = df2.copy()
    df = df.rolling(window=num).max()
    return df


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
    return ts_Max(ts_Mean(df2, mean_window), window)


def ts_MaxStd(df2, window, std_window):
    """Rolling max of a shorter rolling standard deviation."""
    return ts_Max(ts_Stdev(df2, std_window), window)

def ts_Min(df2, num):             # get the min value of last num trading day  
    df = df2.copy()
    df = df.rolling(window=num).min()
    return df


def ts_MinDiff(df2, window):
    """Latest value minus rolling minimum."""
    return df2 - ts_Min(df2, window)

def ts_Delta(df2, num):   
    df = df2.copy()
    df = df - ts_Delay(df,num)
    return df

def ts_Cov(df_y2, df_x2, num):
    y = df_y2.copy()
    x = df_x2.copy()
    return y.rolling(window=num).cov(x)


def ts_Percentage(df2, num):
    """Time-series percentile of the latest value inside each rolling window."""
    df = df2.copy()
    return df.rolling(window=num).rank(pct=True)


def ts_Stdev(df2, num):             # get the min value of last num trading day  
    df = df2.copy()
    df = df.rolling(num).std()
    return df

def ts_Sum(df2, num):
    dfCleaned = df2.copy()
    stds = dfCleaned.rolling(window=num).sum()
    return stds

def ts_Kurtosis(df2, num):
    dfCleaned = df2.copy()
    stds = dfCleaned.rolling(window=num).kurt()
    return stds

def ts_Skewness(df2, num):
    dfCleaned = df2.copy()
    stds = dfCleaned.rolling(window=num).skew()
    return stds

def ts_Median(df2, num):
    dfCleaned = df2.copy()
    stds = dfCleaned.rolling(window=num).median()
    return stds


def ts_AvDiff(df2, window):
    """Latest value minus rolling mean."""
    return df2 - ts_Mean(df2, window)


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


def Sin(df2):
    """Element-wise sine."""
    return np.sin(df2)

# more calculator , see df.rolling
# ===== Stage 1 additional operators =====

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
