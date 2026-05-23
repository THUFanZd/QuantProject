"""Fifteen enhanced factors built from neutralization, fundamentals and Barra.

The file is intentionally isolated from the main factor library. The companion
evaluation script injects these functions into the existing FACTOR_REGISTRY so
the original evaluate_factor.py protocol remains unchanged.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from feature import (
    Abs,
    pn_GroupRank,
    pn_Rank,
    pn_Stand,
    safe_div,
    ts_ChgRate,
    ts_Cov,
    ts_Decay,
    ts_Delay,
    ts_Mean,
    ts_Percentage,
    ts_Stdev,
    ts_Sum,
)
from group_work.factor_lib.factors import read_pickle_bypass


DATA_ROOT: Path | None = None


def set_data_root(path: Path) -> None:
    global DATA_ROOT
    DATA_ROOT = path


def _vroc_12d(dt: dict[str, pd.DataFrame]) -> pd.DataFrame:
    return ts_ChgRate(dt["vol"], 12)


def _turnover(dt: dict[str, pd.DataFrame]) -> pd.DataFrame:
    if "turnover_rate" in dt:
        return dt["turnover_rate"]
    return safe_div(dt["vol"] * 100, dt["float_share"])


def _elg_net(dt: dict[str, pd.DataFrame]) -> pd.DataFrame:
    return dt["buy_elg_amount"] - dt["sell_elg_amount"]


def _f13_opt(dt: dict[str, pd.DataFrame]) -> pd.DataFrame:
    return -ts_Stdev(dt["net_mf_amount"], 5)


def _f18(dt: dict[str, pd.DataFrame], rank_window: int = 10, decay_window: int = 60) -> pd.DataFrame:
    return -ts_Percentage(pn_Rank(dt["close"]), rank_window) * ts_Decay(_vroc_12d(dt), decay_window)


def _f27(dt: dict[str, pd.DataFrame]) -> pd.DataFrame:
    return ts_Decay(ts_Sum(dt["net_mf_amount"], 20), 5) - ts_Decay(_elg_net(dt), 5)


def _f29(dt: dict[str, pd.DataFrame]) -> pd.DataFrame:
    return ts_Decay(ts_Sum(dt["net_mf_amount"], 20), 5) * ts_Stdev(dt["totalRet"], 60)


def _f34(dt: dict[str, pd.DataFrame], rank_vol_window: int, cov_window: int) -> pd.DataFrame:
    close_rank_vol = ts_Stdev(pn_Rank(dt["close"]), rank_vol_window)
    return -ts_Cov(_vroc_12d(dt), close_rank_vol, cov_window)


def _f43(dt: dict[str, pd.DataFrame], short_window: int = 20, long_window: int = 120) -> pd.DataFrame:
    turn = _turnover(dt)
    return -safe_div(ts_Mean(turn, short_window), ts_Mean(turn, long_window))


def _cross_residual(y: pd.DataFrame, x: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(np.nan, index=y.index, columns=y.columns)
    for idx in y.index:
        yy = y.loc[idx]
        xx = x.loc[idx]
        valid = yy.notna() & xx.notna()
        if valid.sum() < 3:
            continue
        xv = xx[valid].astype(float)
        yv = yy[valid].astype(float)
        var = xv.var()
        if pd.isna(var) or var == 0:
            out.loc[idx, valid] = yv - yv.mean()
            continue
        beta = xv.cov(yv) / var
        alpha = yv.mean() - beta * xv.mean()
        out.loc[idx, valid] = yv - (alpha + beta * xv)
    return out


def _group_demean(value: pd.DataFrame, group: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(np.nan, index=value.index, columns=value.columns)
    group = group.reindex(index=value.index, columns=value.columns)
    for idx in value.index:
        vals = value.loc[idx]
        gps = group.loc[idx]
        for _, cols in gps.dropna().groupby(gps.dropna()).groups.items():
            out.loc[idx, cols] = vals.loc[cols] - vals.loc[cols].mean()
    return out


def _roe(dt: dict[str, pd.DataFrame]) -> pd.DataFrame:
    return safe_div(_local_field("NetProfitTTMQ1", dt), _local_field("NetAssetQ1", dt))


def _roa(dt: dict[str, pd.DataFrame]) -> pd.DataFrame:
    return safe_div(_local_field("NetProfitTTMQ1", dt), _local_field("TotalAssetQ1", dt))


def _barra_style(name: str, dt: dict[str, pd.DataFrame]) -> pd.DataFrame:
    if DATA_ROOT is None:
        raise FileNotFoundError("DATA_ROOT is not set for Barra style loading.")
    path = DATA_ROOT / "barra" / "style" / f"{name}.pkl"
    try:
        frame = pd.read_pickle(path)
        frame.index = pd.to_datetime(frame.index)
    except Exception:
        frame = read_pickle_bypass(path)
    idxwgt = pd.read_csv(DATA_ROOT / "idxWgt.csv", index_col=0, parse_dates=True)
    if len(frame.columns) <= len(idxwgt.columns):
        frame.columns = idxwgt.columns[: len(frame.columns)]
    ref = dt["close"]
    return frame.sort_index().reindex(index=ref.index, columns=ref.columns)


def _local_field(name: str, dt: dict[str, pd.DataFrame]) -> pd.DataFrame:
    if name in dt:
        return dt[name]
    if DATA_ROOT is None:
        raise FileNotFoundError(f"DATA_ROOT is not set for field {name!r}.")
    for folder in (DATA_ROOT / "matrix", DATA_ROOT / "finMatrix"):
        path = folder / f"{name}.pkl"
        if not path.exists():
            continue
        try:
            frame = pd.read_pickle(path)
            frame.index = pd.to_datetime(frame.index)
        except Exception:
            frame = read_pickle_bypass(path)
        idxwgt = pd.read_csv(DATA_ROOT / "idxWgt.csv", index_col=0, parse_dates=True)
        if len(frame.columns) <= len(idxwgt.columns):
            frame.columns = idxwgt.columns[: len(frame.columns)]
        ref = dt["close"]
        dt[name] = frame.sort_index().reindex(index=ref.index, columns=ref.columns)
        return dt[name]
    raise FileNotFoundError(f"Cannot find local field {name!r}.")


# 1) Neutralization / orthogonalization enhancements.
def factor_add_01_f34_1530_orth_core34(dt: dict[str, pd.DataFrame]) -> pd.DataFrame:
    return _cross_residual(_f34(dt, 15, 30), _f34(dt, 5, 20))


def factor_add_02_f43_industry_neutral(dt: dict[str, pd.DataFrame]) -> pd.DataFrame:
    return pn_GroupRank(_f43(dt), dt["hy"])


def factor_add_03_f18_orth_core34(dt: dict[str, pd.DataFrame]) -> pd.DataFrame:
    return _cross_residual(_f18(dt, 10, 60), _f34(dt, 5, 20))


def factor_add_04_f27_orth_core13(dt: dict[str, pd.DataFrame]) -> pd.DataFrame:
    return _cross_residual(_f27(dt), _f13_opt(dt))


def factor_add_05_f29_orth_core13(dt: dict[str, pd.DataFrame]) -> pd.DataFrame:
    return _cross_residual(_f29(dt), _f13_opt(dt))


# 2) Fundamental x price-volume / fund-flow enhancements.
def factor_add_06_quality_x_flow(dt: dict[str, pd.DataFrame]) -> pd.DataFrame:
    quality = pn_Rank(_roe(dt))
    flow = pn_Rank(ts_Sum(dt["net_mf_amount"], 20))
    return quality * flow


def factor_add_07_value_x_turnover_reversal(dt: dict[str, pd.DataFrame]) -> pd.DataFrame:
    cheap = 1.0 - pn_Rank(dt["pb"])
    return cheap * pn_Stand(_f43(dt))


def factor_add_08_growth_x_price_volume(dt: dict[str, pd.DataFrame]) -> pd.DataFrame:
    growth = pn_Rank(_local_field("RevenueIncYoY", dt))
    return growth * pn_Stand(_f18(dt, 10, 40))


def factor_add_09_cashflow_yield_lowvol(dt: dict[str, pd.DataFrame]) -> pd.DataFrame:
    cash_yield = pn_Rank(safe_div(_local_field("c_fr_sale_sg", dt), dt["total_mv"]))
    low_vol = 1.0 - pn_Rank(ts_Stdev(dt["totalRet"], 60))
    return cash_yield * low_vol


def factor_add_10_profitability_x_f34(dt: dict[str, pd.DataFrame]) -> pd.DataFrame:
    profitability = pn_Rank(_roa(dt))
    return profitability * pn_Stand(_f34(dt, 15, 30))


# 3) Barra style neutralization / conditional enhancements.
def factor_add_11_f43_low_barra_resvol(dt: dict[str, pd.DataFrame]) -> pd.DataFrame:
    resvol = _barra_style("ResVol", dt)
    return pn_Stand(_f43(dt)) * (1.0 - pn_Rank(resvol))


def factor_add_12_f34_value_barra_btp(dt: dict[str, pd.DataFrame]) -> pd.DataFrame:
    btp = _barra_style("BTP", dt)
    return pn_Stand(_f34(dt, 15, 30)) * pn_Rank(btp)


def factor_add_13_flow_low_barra_beta(dt: dict[str, pd.DataFrame]) -> pd.DataFrame:
    beta = _barra_style("Beta", dt)
    beta_mid = 1.0 - Abs(pn_Rank(beta) - 0.5) * 2.0
    return pn_Stand(ts_Decay(ts_Sum(dt["net_mf_amount"], 20), 5)) * beta_mid


def factor_add_14_f18_low_barra_liquidity(dt: dict[str, pd.DataFrame]) -> pd.DataFrame:
    liquidity = _barra_style("Liquidity", dt)
    return pn_Stand(_f18(dt, 10, 40)) * (1.0 - pn_Rank(liquidity))


def factor_add_15_f43_barra_momentum_neutral(dt: dict[str, pd.DataFrame]) -> pd.DataFrame:
    momentum = _barra_style("Momentum", dt)
    return _cross_residual(_f43(dt), momentum)


FACTOR_ADD_REGISTRY = {
    "factor_add_01_f34_1530_orth_core34": factor_add_01_f34_1530_orth_core34,
    "factor_add_02_f43_industry_neutral": factor_add_02_f43_industry_neutral,
    "factor_add_03_f18_orth_core34": factor_add_03_f18_orth_core34,
    "factor_add_04_f27_orth_core13": factor_add_04_f27_orth_core13,
    "factor_add_05_f29_orth_core13": factor_add_05_f29_orth_core13,
    "factor_add_06_quality_x_flow": factor_add_06_quality_x_flow,
    "factor_add_07_value_x_turnover_reversal": factor_add_07_value_x_turnover_reversal,
    "factor_add_08_growth_x_price_volume": factor_add_08_growth_x_price_volume,
    "factor_add_09_cashflow_yield_lowvol": factor_add_09_cashflow_yield_lowvol,
    "factor_add_10_profitability_x_f34": factor_add_10_profitability_x_f34,
    "factor_add_11_f43_low_barra_resvol": factor_add_11_f43_low_barra_resvol,
    "factor_add_12_f34_value_barra_btp": factor_add_12_f34_value_barra_btp,
    "factor_add_13_flow_low_barra_beta": factor_add_13_flow_low_barra_beta,
    "factor_add_14_f18_low_barra_liquidity": factor_add_14_f18_low_barra_liquidity,
    "factor_add_15_f43_barra_momentum_neutral": factor_add_15_f43_barra_momentum_neutral,
}
