
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

def ts_Min(df2, num):             # get the min value of last num trading day  
    df = df2.copy()
    df = df.rolling(window=num).min()
    return df

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

# more calculator , see df.rolling
