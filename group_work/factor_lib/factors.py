"""Factor implementations translated from source formulas."""

from __future__ import annotations

import pickletools
from pathlib import Path
import sys

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FEATURE_DIR = PROJECT_ROOT / "code" / "stock1800"
COURSE_DATA_DIR = Path(r"C:\Users\lzx\Desktop\研一下\量化\课程资料（中证1000）\stock1000\data")
if str(FEATURE_DIR) not in sys.path:
    sys.path.insert(0, str(FEATURE_DIR))

from feature import (  # noqa: E402
    pn_CrossResidual,
    pn_Rank,
    ts_Cov,
    ts_Delay,
    ts_Delta,
    ts_Mean,
    ts_Percentage,
    ts_Stdev,
    ts_Sum,
)


def read_pickle_bypass(path: Path, n_cols: int | None = None) -> pd.DataFrame:
    """Read pickle file directly using pickletools to bypass version issues.

    Handles multiple formats:
    - Barra style: 2 large blobs (values + dates)
    - Matrix combined: 1 large blob (all data together, like net_mf_amount)
    - Matrix per-stock: many small blobs (one per stock, like close.pkl)
    """
    blobs: list[bytes] = []
    for op, arg, _ in pickletools.genops(path.read_bytes()):
        if op.name in {"BYTEARRAY8", "BINBYTES"} and isinstance(arg, (bytes, bytearray)):
            blobs.append(bytes(arg))

    if len(blobs) == 0:
        raise ValueError(f"Cannot find numeric payloads in {path}")

    # Filter for large blobs (>100KB)
    large_blobs = [b for b in blobs if len(b) > 100000]

    if len(large_blobs) >= 2 and len(large_blobs[1]) < len(large_blobs[0]) // 100:
        # Format 1: Barra style - values blob + dates blob
        values_blob, dates_blob = large_blobs[0], large_blobs[1]
        n_dates = len(dates_blob) // 8
        values = np.frombuffer(values_blob, dtype="<f8").reshape(n_dates, -1)
        date_us = np.frombuffer(dates_blob, dtype="<i8")
        dates = pd.to_datetime(date_us, unit="us")

    elif len(large_blobs) == 1:
        # Format 2: Single combined blob (like net_mf_amount)
        values_blob = large_blobs[0]
        total_values = len(values_blob) // 8
        if n_cols is not None:
            n_dates = total_values // n_cols
        else:
            n_cols = 1000
            n_dates = total_values // n_cols
        values = np.frombuffer(values_blob, dtype="<f8").reshape(n_dates, n_cols)
        # Use approximate date range for CSI1000
        dates = pd.date_range(start="2010-01-04", periods=n_dates, freq="B")

    else:
        # Format 3: Multiple small blobs (one per stock, like close.pkl)
        from collections import Counter
        blob_sizes = [len(b) for b in blobs if len(b) > 1000]
        if not blob_sizes:
            raise ValueError(f"Cannot parse pickle format in {path}")

        # Most common size is the per-stock data size
        size_counts = Counter(blob_sizes)
        common_size = size_counts.most_common(1)[0][0]

        # Extract blobs with common size
        stock_blobs = [b for b in blobs if len(b) == common_size]
        n_dates = common_size // 8
        n_cols = len(stock_blobs)

        # Stack all stock data as columns
        values = np.column_stack([
            np.frombuffer(b, dtype="<f8") for b in stock_blobs
        ])
        dates = pd.date_range(start="2010-01-04", periods=n_dates, freq="B")

    return pd.DataFrame(values, index=dates)


def _require_field(dt: dict[str, pd.DataFrame], key: str) -> pd.DataFrame:
    if key not in dt:
        raise KeyError(f"dt is missing required field: {key}")
    return dt[key]


def factor_42_adjusted_price_reversal(
    dt: dict[str, pd.DataFrame],
    window: int = 30,
    price_key: str = "adj_close",
) -> pd.DataFrame:
    """30-day adjusted-price reversal.

    Source formula:
        -(AF_CLOSE / DELAY(AF_CLOSE, 30) - 1)

    Mapping:
        AF_CLOSE -> dt["adj_close"]
        DELAY    -> feature.ts_Delay
    """

    adj_close = _require_field(dt, price_key)
    delayed_close = ts_Delay(adj_close, window).replace(0, np.nan)
    return -(adj_close / delayed_close - 1.0)


def factor_35_price_spread_momentum(
    dt: dict[str, pd.DataFrame],
    window: int = 10,
    open_key: str = "open",
    close_key: str = "close",
) -> pd.DataFrame:
    """10-day open-close spread multiplied by cross-sectional price momentum rank.

    Source formula:
        (TS_MEAN(OPEN, 10) - TS_MEAN(CLOSE, 10)) * RANK(TS_DELTA(CLOSE, 10))
    """

    open_px = _require_field(dt, open_key)
    close_px = _require_field(dt, close_key)
    spread = ts_Mean(open_px, window) - ts_Mean(close_px, window)
    momentum_rank = pn_Rank(ts_Delta(close_px, window))
    return spread * momentum_rank


def factor_05_volume_price_divergence_cov(
    dt: dict[str, pd.DataFrame],
    delta_window: int = 1,
    cov_window: int = 30,
    volume_key: str = "vol",
    close_key: str = "close",
) -> pd.DataFrame:
    """Negative rolling covariance between volume change and close-price change.

    Source formula:
        TS_COVARIANCE(DELTA(VOLUME, 1), DELTA(CLOSE, 1), 30) * (-1)
    """

    volume = _require_field(dt, volume_key)
    close_px = _require_field(dt, close_key)
    volume_delta = ts_Delta(volume, delta_window)
    close_delta = ts_Delta(close_px, delta_window)
    return -ts_Cov(volume_delta, close_delta, cov_window)


def factor_38_volatility_difference_proxy(
    dt: dict[str, pd.DataFrame],
    percentage_window: int = 5,
    volume_vol_window: int = 60,
    residual_vol_window: int = 20,
    volume_key: str = "vol",
    close_key: str = "close",
) -> pd.DataFrame:
    """Proxy for volatility-difference factor.

    Source formula:
        TS_PERCENTAGE(FACTOR_VOL60D, 5) - TS_PERCENTAGE(FACTOR_TVSD20D, 5)

    Local mapping:
        FACTOR_VOL60D   -> ts_Stdev(dt["vol"], 60)
        FACTOR_TVSD20D  -> ts_Stdev(pn_CrossResidual(dt["close"], dt["vol"]), 20)
    """

    volume = _require_field(dt, volume_key)
    close_px = _require_field(dt, close_key)
    factor_vol60d = ts_Stdev(volume, volume_vol_window)
    residual = pn_CrossResidual(close_px, volume)
    factor_tvsd20d = ts_Stdev(residual, residual_vol_window)
    return ts_Percentage(factor_vol60d, percentage_window) - ts_Percentage(
        factor_tvsd20d, percentage_window
    )


def factor_08_liquidity_stability(
    dt: dict[str, pd.DataFrame],
    window: int = 10,
    amount_key: str = "amount",
) -> pd.DataFrame:
    """Negative 10-day mean of cross-sectional amount rank.

    Source formula:
        -TS_MEAN(RANK(AMOUNT), 10)
    """

    amount = _require_field(dt, amount_key)
    return -ts_Mean(pn_Rank(amount), window)


def _ts_wma(df2: pd.DataFrame, window: int) -> pd.DataFrame:
    """Weighted moving average with linearly decreasing weights.

    Weight pattern: window, window-1, ..., 1 (normalized to sum=1)
    """
    df = df2.copy()
    weights = np.arange(1, window + 1)  # 1, 2, ..., window
    weights = weights / weights.sum()  # normalize
    return df.rolling(window=window).apply(
        lambda x: (x * weights).sum() if len(x) == window else np.nan,
        raw=True
    )


def factor_06_ma_filter_reversal(
    dt: dict[str, pd.DataFrame],
    ma_window: int = 35,
    delta_window: int = 10,
    close_key: str = "close",
) -> pd.DataFrame:
    """MA-filtered reversal factor.

    Source formula:
        (((TS_SUM(CLOSE, 35) / 35) < CLOSE) ? (-1 * DELTA(CLOSE, 10)) : 0)

    Logic: If close > 35-day MA (price above MA), return negative 10-day price change;
            otherwise return 0. Captures reversal when price breaks above MA.
    """

    close_px = _require_field(dt, close_key)
    ma = ts_Sum(close_px, ma_window) / ma_window
    price_above_ma = close_px > ma
    delta_close = ts_Delta(close_px, delta_window)
    return -delta_close.where(price_above_ma, 0)


def factor_41_high_open_momentum_decay(
    dt: dict[str, pd.DataFrame],
    window: int = 5,
    high_key: str = "high",
    open_key: str = "open",
) -> pd.DataFrame:
    """High-open momentum decay factor.

    Source formula:
        -(TS_WMA((HIGH - OPEN), 5))

    Logic: Negative weighted moving average of (high - open).
            High values indicate opening low and rallying intraday.
            The negative sign captures mean reversion.
    """

    high_px = _require_field(dt, high_key)
    open_px = _require_field(dt, open_key)
    high_open_spread = high_px - open_px
    return -_ts_wma(high_open_spread, window)


def _ts_ir(df2: pd.DataFrame, window: int) -> pd.DataFrame:
    """Time-series Information Ratio: rolling mean / rolling std."""
    df = df2.copy()
    rolling_mean = df.rolling(window=window).mean()
    rolling_std = df.rolling(window=window).std()
    return rolling_mean / rolling_std.replace(0, np.nan)


def factor_13_main_fund_stability(
    dt: dict[str, pd.DataFrame],
    window: int = 10,
) -> pd.DataFrame:
    """Main fund flow stability factor.

    Source formula:
        -TS_STDDEV(MAIN_IN_FLOW_V2, 10)

    Local mapping:
        MAIN_IN_FLOW_V2 -> net_mf_amount from course data
    """

    net_mf_path = COURSE_DATA_DIR / "matrix" / "net_mf_amount.pkl"
    net_mf = read_pickle_bypass(net_mf_path, n_cols=1000)
    return -ts_Stdev(net_mf, window)


def factor_26_dual_style_ir_spread(
    dt: dict[str, pd.DataFrame],
    window: int = 20,
) -> pd.DataFrame:
    """Dual style IR spread factor.

    Source formula:
        TS_IR(FACTOR_CNE5_BETA, 20) - TS_IR(FACTOR_CNE5_SIZE, 20)

    Uses Barra style factors from course data.
    """

    beta_path = COURSE_DATA_DIR / "barra" / "style" / "Beta.pkl"
    size_path = COURSE_DATA_DIR / "barra" / "style" / "Size.pkl"

    beta = read_pickle_bypass(beta_path)
    size = read_pickle_bypass(size_path)

    beta_ir = _ts_ir(beta, window)
    size_ir = _ts_ir(size, window)

    return beta_ir - size_ir


def factor_56_cashflow_price_trend(
    dt: dict[str, pd.DataFrame],
    window: int = 60,
) -> pd.DataFrame:
    """Cash flow price trend factor (simplified proxy).

    Source formula:
        RANK_NORMALIZE(RANK(FACTOR_MFI21D) * (FACTOR_CASHOFSALES - TS_MAX_STD(AF_CLOSE, 60, 2)))

    Local mapping (simplified):
        FACTOR_CASHOFSALES -> c_fr_sale_sg / total_mv from course data
        TS_MAX_STD -> ts_Stdev over window
    """

    # Load data from course materials
    cfr_path = COURSE_DATA_DIR / "finMatrix" / "c_fr_sale_sg.pkl"
    total_mv_path = COURSE_DATA_DIR / "matrix" / "total_mv.pkl"
    adj_close_path = COURSE_DATA_DIR / "matrix" / "adj_close.pkl"

    cfr = read_pickle_bypass(cfr_path, n_cols=1000)
    total_mv = read_pickle_bypass(total_mv_path, n_cols=1000)
    adj_close = read_pickle_bypass(adj_close_path, n_cols=1000)

    # Cash flow to sales ratio proxy
    cashofsales = cfr / total_mv.replace(0, np.nan)

    # Price volatility component
    price_vol = ts_Stdev(adj_close, window)

    # Simplified factor: rank of cashofsales minus price volatility
    factor = pn_Rank(cashofsales) - pn_Rank(price_vol)

    return factor


FACTOR_REGISTRY = {
    "factor_05_volume_price_divergence_cov": factor_05_volume_price_divergence_cov,
    "factor_06_ma_filter_reversal": factor_06_ma_filter_reversal,
    "factor_08_liquidity_stability": factor_08_liquidity_stability,
    "factor_13_main_fund_stability": factor_13_main_fund_stability,
    "factor_26_dual_style_ir_spread": factor_26_dual_style_ir_spread,
    "factor_35_price_spread_momentum": factor_35_price_spread_momentum,
    "factor_38_volatility_difference_proxy": factor_38_volatility_difference_proxy,
    "factor_41_high_open_momentum_decay": factor_41_high_open_momentum_decay,
    "factor_42_adjusted_price_reversal": factor_42_adjusted_price_reversal,
    "factor_56_cashflow_price_trend": factor_56_cashflow_price_trend,
}
