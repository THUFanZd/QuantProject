"""Barra data-loading and neutralization helpers used by the Stage-4 backtest."""

from __future__ import annotations

import pickletools
import sys
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FEATURE_DIR = PROJECT_ROOT / "code" / "stock1800"
START_DATE = pd.Timestamp("2017-01-01")
LOAD_START = pd.Timestamp("2015-01-01")
MIN_REGRESSION_OBS = 80

STYLES = [
    "Size",
    "Beta",
    "Momentum",
    "ResVol",
    "NLS",
    "BTP",
    "Liquidity",
    "EY",
    "Growth",
    "Leverage",
]

SW2021_L1_INDUSTRY_MAP = {
    801010: "农林牧渔",
    801030: "基础化工",
    801040: "钢铁",
    801050: "有色金属",
    801080: "电子",
    801110: "家用电器",
    801120: "食品饮料",
    801130: "纺织服饰",
    801140: "轻工制造",
    801150: "医药生物",
    801160: "公用事业",
    801170: "交通运输",
    801180: "房地产",
    801200: "商贸零售",
    801210: "社会服务",
    801230: "综合",
    801710: "建筑材料",
    801720: "建筑装饰",
    801730: "电力设备",
    801740: "国防军工",
    801750: "计算机",
    801760: "传媒",
    801770: "通信",
    801780: "银行",
    801790: "非银金融",
    801880: "汽车",
    801890: "机械设备",
    801950: "煤炭",
    801960: "石油石化",
    801970: "环保",
    801980: "美容护理",
}

BASE_FIELDS = [
    "high",
    "low",
    "net_mf_amount",
    "totalRet",
    "turnover_rate",
    "turnover_rate_f",
    "adj_close",
    "adj_high",
    "adj_low",
    "close",
    "vol",
    "overnightRet",
    "amount",
]
FIN_FIELDS = ["NetProfitTTMQ1", "NetAssetQ1"]

for path in (PROJECT_ROOT, FEATURE_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from feature import pn_TransNorm  # noqa: E402
from group_work.factor_lib import factors as factor_module  # noqa: E402
from group_work.factor_lib.data_loader import read_pickle_bypass  # noqa: E402


def patch_factor_data_root(data_root: Path) -> None:
    """Point lazy factor helpers at the external data environment."""

    factor_module.COURSE_DATA_DIR = data_root
    factor_module.MATRIX_DIR = data_root / "matrix"
    factor_module.FIN_MATRIX_DIR = data_root / "finMatrix"
    for name in ("_stock_codes", "_load_local_field_cached"):
        fn = getattr(factor_module, name, None)
        if hasattr(fn, "cache_clear"):
            fn.cache_clear()


def read_idxwgt(data_root: Path) -> pd.DataFrame:
    idxwgt_path = data_root / "idxWgt.csv"
    if idxwgt_path.exists():
        return pd.read_csv(idxwgt_path, index_col=0, parse_dates=True)
    idxwgt = pd.read_pickle(data_root / "idxWgt.pkl")
    idxwgt.index = pd.to_datetime(idxwgt.index)
    return idxwgt


def align_frame(
    frame: pd.DataFrame,
    idxwgt: pd.DataFrame,
    start: pd.Timestamp = LOAD_START,
) -> pd.DataFrame:
    if len(frame.index) == len(idxwgt.index):
        frame.index = idxwgt.index
    frame.index = pd.to_datetime(frame.index)
    if len(frame.columns) <= len(idxwgt.columns):
        frame.columns = list(idxwgt.columns[: len(frame.columns)])
    frame = frame.sort_index().reindex(columns=idxwgt.columns)
    return frame.loc[frame.index >= start]


def load_float_frame(path: Path, idxwgt: pd.DataFrame) -> pd.DataFrame:
    try:
        frame = pd.read_pickle(path)
    except Exception:
        frame = read_pickle_bypass(path)
    return align_frame(frame, idxwgt)


def load_int_matrix(path: Path, idxwgt: pd.DataFrame) -> pd.DataFrame:
    blobs: list[bytes] = []
    for op, arg, _ in pickletools.genops(path.read_bytes()):
        if op.name in {"BYTEARRAY8", "BINBYTES"} and isinstance(arg, (bytes, bytearray)):
            blobs.append(bytes(arg))
    if not blobs:
        raise ValueError(f"No numeric payload found in {path}")

    lengths = [len(blob) for blob in blobs if len(blob) > 1000]
    common_length = max(set(lengths), key=lengths.count)
    stock_blobs = [blob for blob in blobs if len(blob) == common_length]
    values = np.column_stack([np.frombuffer(blob, dtype="<i8") for blob in stock_blobs])
    frame = pd.DataFrame(values, index=idxwgt.index[: values.shape[0]], columns=idxwgt.columns[: values.shape[1]])
    return align_frame(frame.astype(float), idxwgt).mask(lambda x: x == 0)


def load_barra_style(path: Path, idxwgt: pd.DataFrame) -> pd.DataFrame:
    blobs: list[bytes] = []
    for op, arg, _ in pickletools.genops(path.read_bytes()):
        if op.name in {"BYTEARRAY8", "BINBYTES"} and isinstance(arg, (bytes, bytearray)):
            blobs.append(bytes(arg))
    if len(blobs) < 2:
        return load_float_frame(path, idxwgt)

    value_blob = max(blobs, key=len)
    date_blob = min(blobs, key=len)
    dates = pd.to_datetime(np.frombuffer(date_blob, dtype="<i8"), unit="us")
    values = np.frombuffer(value_blob, dtype="<f8")
    n_dates = len(dates)
    if n_dates == 0 or len(values) % n_dates != 0:
        raise ValueError(f"Cannot infer Barra style shape for {path}")
    n_cols = len(values) // n_dates
    arr = values.reshape(n_cols, n_dates).T
    frame = pd.DataFrame(arr, index=dates, columns=idxwgt.columns[:n_cols])
    return align_frame(frame, idxwgt)


def load_data(data_root: Path) -> tuple[dict[str, pd.DataFrame], pd.DataFrame, pd.DataFrame, dict[str, pd.DataFrame]]:
    full_idxwgt = read_idxwgt(data_root)
    dt: dict[str, pd.DataFrame] = {}
    for field in BASE_FIELDS:
        dt[field] = load_float_frame(data_root / "matrix" / f"{field}.pkl", full_idxwgt)
    for field in FIN_FIELDS:
        dt[field] = load_float_frame(data_root / "finMatrix" / f"{field}.pkl", full_idxwgt)
    dt["hy"] = load_int_matrix(data_root / "matrix" / "hy.pkl", full_idxwgt)

    dt["totalRet"] = dt["totalRet"].mask(dt["totalRet"].abs() > 0.2)
    listed = (dt["vol"].fillna(0).cumsum() > 0).shift(20, fill_value=False).astype(bool)
    idxwgt = full_idxwgt.loc[full_idxwgt.index >= LOAD_START]
    universe_mask = idxwgt.reindex(index=dt["close"].index, columns=dt["close"].columns) == 0
    styles = {
        style: load_barra_style(data_root / "barra" / "style" / f"{style}.pkl", full_idxwgt)
        for style in STYLES
    }
    return dt, listed, universe_mask, styles


def score_factor(raw: pd.DataFrame, universe_mask: pd.DataFrame, listed: pd.DataFrame) -> pd.DataFrame:
    factor = raw.replace([np.inf, -np.inf], np.nan)
    factor = factor.mask(universe_mask).mask(~listed)
    factor = pn_TransNorm(factor).replace([np.inf, -np.inf], np.nan)
    return factor.loc[factor.index >= START_DATE]


def mean_cross_sectional_corr(left: pd.DataFrame, right: pd.DataFrame) -> float:
    return float(left.corrwith(right, axis=1).mean(skipna=True))


def industry_label(code: int) -> str:
    name = SW2021_L1_INDUSTRY_MAP.get(int(code), "未知行业")
    return f"{name}({int(code)})"


def regress_one_factor(
    factor: pd.DataFrame,
    shifted_styles: dict[str, pd.DataFrame],
    industry: pd.DataFrame,
    industry_codes: list[int],
) -> tuple[pd.DataFrame, pd.Series, pd.Series, pd.Series]:
    residual = pd.DataFrame(np.nan, index=factor.index, columns=factor.columns)
    r2 = pd.Series(np.nan, index=factor.index)
    alpha = pd.Series(np.nan, index=factor.index)
    nobs = pd.Series(0.0, index=factor.index)

    style_arrays = [shifted_styles[style].to_numpy(dtype=float, copy=False) for style in STYLES]
    y_array = factor.to_numpy(dtype=float, copy=False)
    ind_array = industry.to_numpy(dtype=float, copy=False)
    dummy_codes = np.array(industry_codes[1:], dtype=float)

    for i, date in enumerate(factor.index):
        y = y_array[i]
        ind = ind_array[i]
        valid = np.isfinite(y) & np.isfinite(ind)
        for arr in style_arrays:
            valid &= np.isfinite(arr[i])
        if int(valid.sum()) < max(MIN_REGRESSION_OBS, len(STYLES) + len(dummy_codes) + 5):
            continue

        yv = y[valid]
        style_values = np.column_stack([arr[i, valid] for arr in style_arrays])
        labels = ind[valid]
        dummies = (labels[:, None] == dummy_codes[None, :]).astype(float)
        x = np.column_stack([np.ones(len(yv)), style_values, dummies])
        try:
            beta, *_ = np.linalg.lstsq(x, yv, rcond=None)
        except np.linalg.LinAlgError:
            continue

        fitted = x @ beta
        eps = yv - fitted
        tss = float(np.sum((yv - yv.mean()) ** 2))
        if tss > 0:
            r2.loc[date] = min(1.0, max(0.0, 1.0 - float(np.sum(eps**2)) / tss))
        alpha.loc[date] = float(beta[0])
        nobs.loc[date] = float(len(yv))
        residual.iloc[i, np.flatnonzero(valid)] = eps

    return residual, r2, alpha, nobs
