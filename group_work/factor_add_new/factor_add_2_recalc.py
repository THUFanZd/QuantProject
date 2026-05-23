"""Three recreated factor_add2 factors that passed AR/SR screening."""

from __future__ import annotations

import pandas as pd

from feature import pn_GroupRank, pn_Rank, ts_ChgRate, ts_Cov, ts_Decay, ts_Percentage, ts_Stdev


def _vroc(dt: dict[str, pd.DataFrame], window: int = 12) -> pd.DataFrame:
    return ts_ChgRate(dt["vol"], window)


def _f34(dt: dict[str, pd.DataFrame], rank_vol_window: int, cov_window: int) -> pd.DataFrame:
    close_rank_vol = ts_Stdev(pn_Rank(dt["close"]), rank_vol_window)
    return -ts_Cov(_vroc(dt, 12), close_rank_vol, cov_window)


def _f18(dt: dict[str, pd.DataFrame], rank_window: int, decay_window: int) -> pd.DataFrame:
    return -ts_Percentage(pn_Rank(dt["close"]), rank_window) * ts_Decay(_vroc(dt, 12), decay_window)


def factor_add2_adj_05_f34_15_25_industry(dt: dict[str, pd.DataFrame]) -> pd.DataFrame:
    return pn_GroupRank(_f34(dt, rank_vol_window=15, cov_window=25), dt["hy"])


def factor_add2_adj_07_f18_decay30_industry(dt: dict[str, pd.DataFrame]) -> pd.DataFrame:
    return pn_GroupRank(_f18(dt, rank_window=10, decay_window=30), dt["hy"])


def factor_add2_adj_04_f34_10_30_industry(dt: dict[str, pd.DataFrame]) -> pd.DataFrame:
    return pn_GroupRank(_f34(dt, rank_vol_window=10, cov_window=30), dt["hy"])


FACTOR_ADD_2_RECALC_REGISTRY = {
    "factor_add2_adj_05_f34_15_25_industry": factor_add2_adj_05_f34_15_25_industry,
    "factor_add2_adj_07_f18_decay30_industry": factor_add2_adj_07_f18_decay30_industry,
    "factor_add2_adj_04_f34_10_30_industry": factor_add2_adj_04_f34_10_30_industry,
}
