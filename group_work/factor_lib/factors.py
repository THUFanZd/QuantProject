"""Factor implementations translated from source formulas."""

from __future__ import annotations

import pickletools
from functools import lru_cache
from pathlib import Path
import sys

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FEATURE_DIR = PROJECT_ROOT / "code" / "stock1800"
COURSE_DATA_DIR = PROJECT_ROOT / "data_1800" / "stock1000" / "data"
MATRIX_DIR = COURSE_DATA_DIR / "matrix"
FIN_MATRIX_DIR = COURSE_DATA_DIR / "finMatrix"
if str(FEATURE_DIR) not in sys.path:
    sys.path.insert(0, str(FEATURE_DIR))

from feature import (  # noqa: E402
    Abs,
    Log,
    Round,
    Sin,
    SignedPower,
    SignedSqrt,
    pn_CrossResidual,
    pn_CSPct,
    pn_CSSkew,
    pn_GroupRank,
    pn_GroupStdev,
    pn_Rank,
    pn_Stand,
    safe_div,
    ts_ChgRate,
    ts_Corr,
    ts_Cov,
    ts_Decay,
    ts_Delay,
    ts_Delta,
    ts_EMA,
    ts_IR,
    ts_Kurtosis,
    ts_Max,
    ts_MaxMean,
    ts_MaxDrawdownAbs,
    ts_MaxStd,
    ts_Mean,
    ts_Median,
    ts_Min,
    ts_MinDiff,
    ts_Percentage,
    ts_Rank,
    ts_Stdev,
    ts_Sum,
    ts_TopKSum,
    ts_WMA,
    ts_AvDiff,
    Winsorize,
)


def read_pickle_bypass(path: Path, n_cols: int | None = None) -> pd.DataFrame:
    """Read pickle file directly using pickletools to bypass version issues.

    Handles multiple formats:
    - Barra style: 2 blobs (values + dates), dates blob is smaller
    - Matrix combined: 1 large blob (all data together, like net_mf_amount)
    - Matrix per-stock: many small blobs (one per stock, like close.pkl)
    """
    blobs: list[bytes] = []
    for op, arg, _ in pickletools.genops(path.read_bytes()):
        if op.name in {"BYTEARRAY8", "BINBYTES"} and isinstance(arg, (bytes, bytearray)):
            blobs.append(bytes(arg))

    if len(blobs) == 0:
        raise ValueError(f"Cannot find numeric payloads in {path}")

    # Check if this is Barra style (2 blobs: values + dates)
    # Values blob is large, dates blob is smaller
    if len(blobs) >= 2 and len(blobs[1]) < len(blobs[0]) // 100:
        values_blob, dates_blob = blobs[0], blobs[1]
        n_dates = len(dates_blob) // 8
        values = np.frombuffer(values_blob, dtype="<f8").reshape(n_dates, -1)
        date_us = np.frombuffer(dates_blob, dtype="<i8")
        dates = pd.to_datetime(date_us, unit="us")
        return pd.DataFrame(values, index=dates)

    # Filter for large blobs (>100KB) for other formats
    large_blobs = [b for b in blobs if len(b) > 100000]

    if len(large_blobs) == 1:
        # Single combined blob (like net_mf_amount)
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
        return pd.DataFrame(values, index=dates)

    # Multiple small blobs (one per stock, like close.pkl)
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
        if key == "vwap":
            dt[key] = safe_div(_require_field(dt, "amount"), _require_field(dt, "vol"))
        else:
            dt[key] = _align_to_dt(_load_local_field(key), dt)
    return dt[key]


@lru_cache(maxsize=1)
def _stock_codes() -> tuple[str, ...]:
    idxwgt_path = COURSE_DATA_DIR / "idxWgt.csv"
    if not idxwgt_path.exists():
        return ()
    idxwgt = pd.read_csv(idxwgt_path, index_col=0, parse_dates=True)
    return tuple(idxwgt.columns.tolist())


@lru_cache(maxsize=None)
def _load_local_field_cached(key: str) -> pd.DataFrame:
    for folder, n_cols in ((MATRIX_DIR, 1000), (FIN_MATRIX_DIR, None)):
        path = folder / f"{key}.pkl"
        if not path.exists():
            continue
        try:
            frame = pd.read_pickle(path)
            frame.index = pd.to_datetime(frame.index)
        except Exception:
            frame = read_pickle_bypass(path, n_cols=n_cols)
        frame = frame.sort_index()
        codes = _stock_codes()
        if codes and len(frame.columns) <= len(codes):
            frame.columns = list(codes[: len(frame.columns)])
        return frame
    raise FileNotFoundError(f"Cannot find local field {key!r} in matrix or finMatrix")


def _load_local_field(key: str) -> pd.DataFrame:
    return _load_local_field_cached(key).copy()


def _align_to_dt(frame: pd.DataFrame, dt: dict[str, pd.DataFrame]) -> pd.DataFrame:
    if not dt:
        return frame
    ref_field = next(iter(dt.values()))
    return frame.reindex(index=ref_field.index, columns=ref_field.columns)


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

    net_mf = _require_field(dt, "net_mf_amount")
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

    # Load Barra style factors
    beta_path = COURSE_DATA_DIR / "barra" / "style" / "Beta.pkl"
    size_path = COURSE_DATA_DIR / "barra" / "style" / "Size.pkl"

    beta = read_pickle_bypass(beta_path)
    size = read_pickle_bypass(size_path)

    # Get stock codes from idxWgt.csv for alignment
    idxwgt_path = COURSE_DATA_DIR / "idxWgt.csv"
    idxwgt = pd.read_csv(idxwgt_path, index_col=0, parse_dates=True)
    stock_codes = idxwgt.columns

    # Assign stock codes as column names
    beta.columns = stock_codes[:len(beta.columns)]
    size.columns = stock_codes[:len(size.columns)]

    # Align dates with the input data
    if dt:
        ref_field = list(dt.values())[0]
        beta = beta.reindex(index=ref_field.index, columns=ref_field.columns)
        size = size.reindex(index=ref_field.index, columns=ref_field.columns)

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

    cashofsales = safe_div(_require_field(dt, "c_fr_sale_sg"), _require_field(dt, "total_mv"))
    price_vol = ts_Stdev(_require_field(dt, "adj_close"), window)
    return pn_Rank(cashofsales) - pn_Rank(price_vol)

def _turn_rate(dt: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Use local turnover when available, otherwise construct a turnover proxy."""

    for key in ("turnover_rate", "turnover_rate_f"):
        try:
            return _require_field(dt, key)
        except (FileNotFoundError, KeyError):
            continue
    return safe_div(_require_field(dt, "vol") * 100, _require_field(dt, "float_share"))


def _main_flow_20d(dt: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Proxy MAIN_IN_FLOW_20D_V2 with 20-day sum of local main net fund flow."""

    return ts_Sum(_require_field(dt, "net_mf_amount"), 20)


def _elg_net_amount(dt: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Proxy SLARGE_IN_FLOW_V2 with extra-large buy amount minus sell amount."""

    return _require_field(dt, "buy_elg_amount") - _require_field(dt, "sell_elg_amount")


def _lg_net_amount(dt: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Proxy large-order net fund flow with large buy amount minus sell amount."""

    return _require_field(dt, "buy_lg_amount") - _require_field(dt, "sell_lg_amount")


def _vroc_12d(dt: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Proxy FACTOR_VROC12D with 12-day volume change rate."""

    return ts_ChgRate(_require_field(dt, "vol"), 12)


def _tvsd_20d(dt: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Proxy FACTOR_TVSD20D with 20-day close-volume residual volatility."""

    residual = pn_CrossResidual(_require_field(dt, "close"), _require_field(dt, "vol"))
    return ts_Stdev(residual, 20)


def _volatility_60d(dt: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Proxy FACTOR_VOL60D in risk-volatility contexts with 60-day return stdev."""

    return ts_Stdev(_require_field(dt, "totalRet"), 60)


def factor_01_residual_volatility(
    dt: dict[str, pd.DataFrame],
    window: int = 20,
    close_key: str = "close",
    volume_key: str = "vol",
) -> pd.DataFrame:
    """Residual volatility factor.

    Source formula:
        -TS_STDDEV(CS_REGRESSION(CLOSE, VOLUME, OUT_TYPE=0), 20)
    """

    close_px = _require_field(dt, close_key)
    volume = _require_field(dt, volume_key)
    residual = pn_CrossResidual(close_px, volume)
    return -ts_Stdev(residual, window)


def factor_02_volume_amount_efficiency(
    dt: dict[str, pd.DataFrame],
    window: int = 30,
    volume_key: str = "vol",
    amount_key: str = "amount",
) -> pd.DataFrame:
    """Volume-amount efficiency factor.

    Source formula:
        RANK(TS_SUM(VOLUME, 30)) / RANK(TS_SUM(AMOUNT, 30))
    """

    volume = _require_field(dt, volume_key)
    amount = _require_field(dt, amount_key)
    return safe_div(pn_Rank(ts_Sum(volume, window)), pn_Rank(ts_Sum(amount, window)))


def factor_03_turnover_volatility_momentum(
    dt: dict[str, pd.DataFrame],
    turnover_window: int = 14,
    price_rank_window: int = 30,
) -> pd.DataFrame:
    """Turnover-volatility momentum proxy.

    Source formula:
        -SIGNED_POWER(RANK(TS_STDDEV(TURN_RATE, 14)), 2) * TS_RANK(CLOSE, 30)
    """

    turnover = _turn_rate(dt)
    close_px = _require_field(dt, "close")
    return -SignedPower(pn_Rank(ts_Stdev(turnover, turnover_window)), 2) * ts_Rank(
        close_px, price_rank_window
    )


def factor_04_reversal_turnover_enhanced(
    dt: dict[str, pd.DataFrame],
    window: int = 5,
) -> pd.DataFrame:
    """Reversal factor enhanced by turnover proxy.

    Source formula:
        -(AF_CLOSE / DELAY(AF_CLOSE, 5) * TURN_RATE)
    """

    adj_close = _require_field(dt, "adj_close")
    turnover = _turn_rate(dt)
    return -safe_div(adj_close, ts_Delay(adj_close, window)) * turnover


def factor_07_price_volume_deviation_vol(
    dt: dict[str, pd.DataFrame],
    window: int = 10,
) -> pd.DataFrame:
    """Price-volume deviation volatility factor.

    Source formula:
        -TS_STDDEV((CLOSE - VWAP) * VOLUME, 10)
    """

    close_px = _require_field(dt, "close")
    vwap = _require_field(dt, "vwap")
    volume = _require_field(dt, "vol")
    return -ts_Stdev((close_px - vwap) * volume, window)


def factor_09_vol_adjusted_reversal(
    dt: dict[str, pd.DataFrame],
    window: int = 30,
) -> pd.DataFrame:
    """Volatility-adjusted reversal factor.

    Source formula:
        -TS_MEAN(SIGNEDPOWER(CHANGE_PCT, 2), 30)
    """

    total_ret = _require_field(dt, "totalRet")
    return -ts_Mean(SignedPower(total_ret, 2), window)


def factor_10_deviation_volume_weighted(
    dt: dict[str, pd.DataFrame],
    window: int = 20,
) -> pd.DataFrame:
    """Moving-average deviation weighted by volume rank."""

    close_px = _require_field(dt, "close")
    volume = _require_field(dt, "vol")
    return (ts_Mean(close_px, window) - close_px) * pn_Rank(volume)


def factor_12_turnover_volatility(
    dt: dict[str, pd.DataFrame],
    window: int = 15,
) -> pd.DataFrame:
    """Negative turnover volatility proxy."""

    return -ts_Stdev(_turn_rate(dt), window)


def factor_14_main_fund_peak_reverse_rank(
    dt: dict[str, pd.DataFrame],
    window: int = 10,
) -> pd.DataFrame:
    """Reverse rank of recent peak main fund inflow."""

    net_mf = _require_field(dt, "net_mf_amount")
    return -pn_Rank(ts_Max(net_mf, window))


def factor_15_multi_dimensional_reversal(
    dt: dict[str, pd.DataFrame],
    window: int = 20,
) -> pd.DataFrame:
    """Multi-dimensional reversal proxy using price, volume and turnover."""

    close_px = _require_field(dt, "close")
    volume = _require_field(dt, "vol")
    turnover = _turn_rate(dt)
    price_strength = pn_Rank(safe_div(close_px, ts_Mean(close_px, window)))
    volume_strength = pn_Rank(ts_Mean(volume, window))
    turnover_strength = pn_Rank(ts_Mean(turnover, window))
    return -price_strength * volume_strength * turnover_strength


def factor_16_price_volume_volatility_negative(
    dt: dict[str, pd.DataFrame],
    window: int = 10,
) -> pd.DataFrame:
    """Negative price-volume volatility co-movement factor."""

    close_px = _require_field(dt, "close")
    volume = _require_field(dt, "vol")
    return -pn_Rank(ts_Stdev(close_px, window)) * pn_Rank(ts_Stdev(volume, window))


def factor_17_price_fund_volatility_negative(
    dt: dict[str, pd.DataFrame],
    window: int = 10,
) -> pd.DataFrame:
    """Negative price and fund-flow volatility co-movement proxy."""

    close_px = _require_field(dt, "close")
    net_mf = _require_field(dt, "net_mf_amount")
    return -pn_Rank(ts_Stdev(close_px, window)) * pn_Rank(ts_Stdev(net_mf, window))


def factor_11_volatility_turnover_coupling(
    dt: dict[str, pd.DataFrame],
    window: int = 15,
) -> pd.DataFrame:
    """Volatility-turnover coupling factor.

    Source formula:
        SCALE(RANK(TS_STDDEV(CLOSE, 15))) * -1 * TURN_RATE
    """

    close_px = _require_field(dt, "close")
    return -pn_Stand(pn_Rank(ts_Stdev(close_px, window))) * _turn_rate(dt)


def factor_18_price_volume_decay_synergy(
    dt: dict[str, pd.DataFrame],
    rank_window: int = 10,
    vroc_window: int = 12,
    decay_window: int = 60,
) -> pd.DataFrame:
    """Price-volume decay synergy proxy.

    FACTOR_VROC12D is not stored locally, so it is derived from volume change.
    """

    close_px = _require_field(dt, "close")
    vroc = ts_ChgRate(_require_field(dt, "vol"), vroc_window)
    return -ts_Percentage(pn_Rank(close_px), rank_window) * ts_Decay(vroc, decay_window)


def factor_19_price_momentum_fund_volatility_reverse(
    dt: dict[str, pd.DataFrame],
    window: int = 15,
) -> pd.DataFrame:
    """Reverse coupling between price momentum and fund-flow volatility."""

    adj_close = _require_field(dt, "adj_close")
    net_mf = _require_field(dt, "net_mf_amount")
    price_mom = pn_Rank(safe_div(adj_close, ts_Delay(adj_close, window)))
    fund_vol = pn_Rank(ts_Stdev(net_mf, window))
    return -price_mom * fund_vol


def factor_20_main_flow_decay(
    dt: dict[str, pd.DataFrame],
    decay_window: int = 10,
) -> pd.DataFrame:
    """Main-fund-flow decay proxy using local net main fund amount."""

    return ts_Decay(_main_flow_20d(dt), decay_window)


def factor_23_main_flow_decay_percentage(
    dt: dict[str, pd.DataFrame],
    decay_window: int = 6,
    pct_window: int = 3,
) -> pd.DataFrame:
    """Time-series percentage of decayed main-fund-flow proxy."""

    return ts_Percentage(ts_Decay(_main_flow_20d(dt), decay_window), pct_window)


def factor_24_main_elg_flow_diff_decay(
    dt: dict[str, pd.DataFrame],
    decay_window: int = 15,
) -> pd.DataFrame:
    """Decayed rank of main fund flow minus extra-large order-flow proxy."""

    return ts_Decay(pn_Rank(_main_flow_20d(dt) - _elg_net_amount(dt)), decay_window)


def factor_25_main_flow_volatility_momentum(
    dt: dict[str, pd.DataFrame],
    pct_window: int = 10,
) -> pd.DataFrame:
    """Main-fund-flow percentile coupled with 60-day return volatility."""

    return ts_Percentage(_main_flow_20d(dt), pct_window) * _volatility_60d(dt)


def factor_27_main_elg_flow_diff_decay(
    dt: dict[str, pd.DataFrame],
    decay_window: int = 5,
) -> pd.DataFrame:
    """Difference between decayed main fund flow and extra-large flow proxies."""

    return ts_Decay(_main_flow_20d(dt), decay_window) - ts_Decay(_elg_net_amount(dt), decay_window)


def factor_29_main_flow_volatility_decay(
    dt: dict[str, pd.DataFrame],
    decay_window: int = 10,
) -> pd.DataFrame:
    """Decayed main-fund-flow proxy coupled with 60-day return volatility."""

    return ts_Decay(_main_flow_20d(dt), decay_window) * _volatility_60d(dt)


def factor_30_volatility_main_flow_momentum(
    dt: dict[str, pd.DataFrame],
    decay_window: int = 10,
    pct_window: int = 10,
) -> pd.DataFrame:
    """Decayed 60-day volatility coupled with main-fund-flow percentile."""

    return ts_Decay(_volatility_60d(dt), decay_window) * ts_Percentage(
        _main_flow_20d(dt), pct_window
    )


def factor_22_rank_momentum_reversal(
    dt: dict[str, pd.DataFrame],
    window: int = 40,
) -> pd.DataFrame:
    """Rank momentum reversal factor."""

    adj_close = _require_field(dt, "adj_close")
    return -ts_Sum(ts_Delta(pn_Rank(adj_close), 1), window)


def factor_28_main_elg_flow_synergy(
    dt: dict[str, pd.DataFrame],
    main_window: int = 20,
    pct_window: int = 30,
    decay_window: int = 15,
) -> pd.DataFrame:
    """Main and extra-large order flow synergy proxy."""

    return pn_Rank(
        ts_Percentage(_main_flow_20d(dt), pct_window)
        * ts_Decay(_elg_net_amount(dt), decay_window)
    )


def factor_31_main_elg_flow_rank_diff_decay(
    dt: dict[str, pd.DataFrame],
    main_window: int = 20,
    decay_window: int = 15,
) -> pd.DataFrame:
    """Decayed rank difference between main fund flow and extra-large order flow."""

    return ts_Decay(
        Abs(pn_Rank(_main_flow_20d(dt))) - Abs(pn_Rank(_elg_net_amount(dt))),
        decay_window,
    )


def factor_32_momentum_flow_composite(
    dt: dict[str, pd.DataFrame],
    decay_window: int = 10,
) -> pd.DataFrame:
    """Composite momentum-flow proxy.

    FACTOR_VROC12D is derived from volume change; MAIN_IN_FLOW_20D_V2 uses
    20-day local main net fund flow.
    """

    return ts_Decay(_vroc_12d(dt), decay_window) + ts_Decay(_main_flow_20d(dt), decay_window)


def factor_33_reinstatement_residual_vol_ratio(
    dt: dict[str, pd.DataFrame],
    reinstatement_window: int = 60,
    stdev_window: int = 35,
) -> pd.DataFrame:
    """Proxy for reinstatement-change volatility over residual-volatility ratio."""

    adj_ret = ts_ChgRate(_require_field(dt, "adj_close"), reinstatement_window)
    return safe_div(ts_Stdev(adj_ret, stdev_window), ts_Stdev(_tvsd_20d(dt), stdev_window))


def factor_34_reverse_vroc_rank_vol_cov(
    dt: dict[str, pd.DataFrame],
    rank_vol_window: int = 15,
    cov_window: int = 20,
) -> pd.DataFrame:
    """Reverse covariance of volume-change rate and close-rank volatility."""

    close_rank_vol = ts_Stdev(pn_Rank(_require_field(dt, "close")), rank_vol_window)
    return -ts_Cov(_vroc_12d(dt), close_rank_vol, cov_window)


def factor_36_short_vol_adjusted_return(
    dt: dict[str, pd.DataFrame],
    window: int = 15,
) -> pd.DataFrame:
    """Short-term volatility-adjusted return factor."""

    close_px = _require_field(dt, "close")
    open_px = _require_field(dt, "open")
    return -pn_Rank(ts_Sum(close_px - open_px, window)) * pn_Rank(ts_Stdev(close_px, window))


def factor_37_volume_stable_close(
    dt: dict[str, pd.DataFrame],
    window: int = 10,
) -> pd.DataFrame:
    """Volume preference adjusted by close-price stability."""

    volume = _require_field(dt, "vol")
    close_px = _require_field(dt, "close")
    return pn_Rank(volume) * (1 - pn_Rank(ts_Stdev(close_px, window)))


def factor_39_reverse_price_volume_rank(
    dt: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """Reverse product of close-price rank and volume rank."""

    close_px = _require_field(dt, "close")
    volume = _require_field(dt, "vol")
    return -pn_Rank(close_px) * pn_Rank(volume)


def factor_40_fund_flow_max_drawdown(
    dt: dict[str, pd.DataFrame],
    window: int = 15,
) -> pd.DataFrame:
    """Negative rolling maximum drawdown of fund flow."""

    net_mf = _require_field(dt, "net_mf_amount")
    return -ts_MaxDrawdownAbs(net_mf, window)


def factor_43_turnover_relative_strength_reversal(
    dt: dict[str, pd.DataFrame],
    short_window: int = 20,
    long_window: int = 120,
) -> pd.DataFrame:
    """Turnover relative strength reversal proxy."""

    turnover = _turn_rate(dt)
    return -safe_div(ts_Mean(turnover, short_window), ts_Mean(turnover, long_window))


def factor_44_volume_divergence_composite_momentum(
    dt: dict[str, pd.DataFrame],
    mean_window: int = 15,
    corr_window: int = 10,
) -> pd.DataFrame:
    """Composite price-volume divergence momentum proxy."""

    close_px = _require_field(dt, "close")
    volume = _require_field(dt, "vol")
    total_ret = _require_field(dt, "totalRet")
    turnover = _turn_rate(dt)
    corr_part = pn_Rank(ts_Corr(pn_Rank(ts_Mean(close_px, mean_window)), pn_Rank(ts_Mean(volume, mean_window)), corr_window))
    ret_part = pn_Rank(ts_Mean(total_ret, mean_window))
    turnover_part = pn_Rank(ts_Mean(turnover, mean_window))
    volume_part = pn_Rank(ts_Mean(volume, mean_window))
    return -corr_part * ret_part * turnover_part * volume_part


def factor_45_log_momentum_reverse_rank(
    dt: dict[str, pd.DataFrame],
    short_window: int = 15,
    long_window: int = 252,
) -> pd.DataFrame:
    """Reverse rank of logged composite momentum proxy.

    FACTOR_ROCTTM is not stored locally, so 252-day adjusted-close change is
    used as a long-horizon momentum proxy.
    """

    close_ret = ts_ChgRate(_require_field(dt, "close"), short_window)
    roc_ttm_proxy = ts_ChgRate(_require_field(dt, "adj_close"), long_window)
    return -pn_Rank(pn_Stand(Log(1 + close_ret + roc_ttm_proxy)))


def factor_46_price_momentum_decay_reversal(
    dt: dict[str, pd.DataFrame],
    window: int = 20,
    top_k: int = 5,
) -> pd.DataFrame:
    """Composite price-momentum decay and reversal factor."""

    close_px = _require_field(dt, "close")
    high_px = _require_field(dt, "high")
    location = ts_Rank(close_px, window)
    spread = ts_TopKSum(high_px, window, top_k) - ts_Median(close_px, window)
    return -(location * (spread + ts_AvDiff(close_px, window)))


def factor_47_nonlinear_volume_price_extreme_reversal(
    dt: dict[str, pd.DataFrame],
    poly_window: int = 30,
    kurt_window: int = 20,
    kurt_top_window: int = 3,
) -> pd.DataFrame:
    """Proxy for nonlinear volume-price extreme reversal.

    The source TS_POLY_REGRESSION output is under-specified, so this uses the
    rolling close-volume and close-volume-squared correlations as a tractable
    nonlinear relation proxy.
    """

    close_px = _require_field(dt, "close")
    volume = _require_field(dt, "vol")
    total_ret = _require_field(dt, "totalRet")
    nonlinear_relation = ts_Corr(close_px, volume, poly_window) + ts_Corr(
        close_px, volume * volume, poly_window
    )
    kurtosis_spike = ts_Max(ts_Kurtosis(total_ret, kurt_window), kurt_top_window)
    return -((nonlinear_relation + kurtosis_spike) * SignedSqrt(volume))


def factor_48_turnover_adjusted_abnormal_price_momentum(
    dt: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """Turnover-adjusted abnormal price momentum proxy."""

    adj_close = _require_field(dt, "adj_close")
    turnover = _turn_rate(dt)
    x = -safe_div(1, turnover)
    residual = pn_CrossResidual(adj_close, x)
    return -pn_Rank(Log(1 + Abs(residual)))


def factor_49_volatility_trend_composite(
    dt: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """Volatility trend composite proxy."""

    close_px = _require_field(dt, "close")
    total_ret = _require_field(dt, "totalRet")
    trend = Round(safe_div(ts_EMA(close_px, 10), ts_Mean(close_px, 5)))
    vol_spread = ts_Stdev(total_ret, 120) - ts_Stdev(total_ret, 20)
    ir_spread = ts_IR(total_ret, 120) - ts_IR(total_ret, 20)
    return trend * vol_spread + ir_spread


def factor_50_reverse_standardized_decay_volume_price(
    dt: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """Reverse standardized maximum decayed volume-price composite proxy."""

    total_ret = _require_field(dt, "totalRet")
    volume = _require_field(dt, "vol")
    raw = ts_Max(ts_Decay(total_ret, 20) * Log(volume + 1), 3)
    return -pn_Stand(raw)


def factor_51_nonlinear_price_volume_flow(
    dt: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """Nonlinear price-volume-fund-flow proxy."""

    adj_close = _require_field(dt, "adj_close")
    returns = safe_div(adj_close, ts_Delay(adj_close, 1)) - 1
    vwap = _require_field(dt, "vwap")
    main_flow_10d = ts_Sum(_require_field(dt, "net_mf_amount"), 10)
    term_flow = (
        Sin(ts_Mean(returns, 5))
        * pn_CSSkew(vwap)
        * ts_Median(main_flow_10d, 20)
    )

    price_range = _require_field(dt, "adj_high") - _require_field(dt, "adj_low")
    volume = _require_field(dt, "vol")
    term_range_volume = Log(1 + ts_MaxStd(price_range, 60, 3)) * safe_div(
        ts_MaxMean(volume, 20, 5),
        ts_Mean(volume, 20),
    )
    return -(term_flow + term_range_volume)


def factor_53_price_flow_cross_quantile(
    dt: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """Price-flow cross-sectional quantile proxy."""

    vwap = _require_field(dt, "vwap")
    adj_high = _require_field(dt, "adj_high")
    price_part = ts_MinDiff(vwap + ts_MinDiff(adj_high, 10), 15)
    institutional_flow = ts_Sum(_lg_net_amount(dt) + _elg_net_amount(dt), 10)
    flow_part = pn_CSPct(_main_flow_20d(dt) + institutional_flow, 0.8)
    return -pn_Rank(Round(price_part * flow_part))


def factor_54_industry_fund_quality_reverse(
    dt: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """Industry main-fund rank adjusted by profitability-quality proxy."""

    industry = _require_field(dt, "hy")
    roe_proxy = safe_div(_require_field(dt, "NetProfitTTMQ1"), _require_field(dt, "NetAssetQ1"))
    roa_proxy = safe_div(_require_field(dt, "NetProfitTTMQ1"), _require_field(dt, "TotalAssetQ1"))
    quality = roe_proxy - ts_Min(ts_Delta(roa_proxy, 250), 250)
    return -pn_Rank(pn_GroupRank(_main_flow_20d(dt), industry) - pn_CSPct(quality, 0.5))


def factor_add_06_quality_x_flow(
    dt: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """Screened add-on factor: profitability quality crossed with main fund flow."""

    quality = pn_Rank(safe_div(_require_field(dt, "NetProfitTTMQ1"), _require_field(dt, "NetAssetQ1")))
    flow = pn_Rank(_main_flow_20d(dt))
    return quality * flow


def factor_opt_01_residual_volatility_w5(dt: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Optimized 5-day variant of residual volatility for stage-2 screening."""

    return factor_01_residual_volatility(dt, window=5)


def factor_opt_01_residual_volatility_w10(dt: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Optimized 10-day variant of residual volatility for stage-2 screening."""

    return factor_01_residual_volatility(dt, window=10)


def factor_opt_05_volume_price_divergence_cov_1_20(
    dt: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """Optimized volume-price covariance variant with 1-day deltas and 20-day covariance."""

    return factor_05_volume_price_divergence_cov(dt, delta_window=1, cov_window=20)


def factor_opt_07_price_volume_deviation_vol_w15(
    dt: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """Optimized 15-day variant of price-volume deviation volatility."""

    return factor_07_price_volume_deviation_vol(dt, window=15)


def factor_opt_13_main_fund_stability_w5(dt: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Optimized 5-day main-fund stability variant."""

    return factor_13_main_fund_stability(dt, window=5)


def factor_opt_33_reinstatement_residual_vol_ratio_40_20(
    dt: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """Optimized reinstatement/residual-volatility ratio using 40-day return and 20-day stdev."""

    return factor_33_reinstatement_residual_vol_ratio(
        dt,
        reinstatement_window=40,
        stdev_window=20,
    )


def factor_opt_33_reinstatement_residual_vol_ratio_80_20(
    dt: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """Optimized reinstatement/residual-volatility ratio using 80-day return and 20-day stdev."""

    return factor_33_reinstatement_residual_vol_ratio(
        dt,
        reinstatement_window=80,
        stdev_window=20,
    )


def factor_opt_34_reverse_vroc_rank_vol_cov_5_20(
    dt: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """Optimized reverse VROC/rank-volatility covariance variant."""

    return factor_34_reverse_vroc_rank_vol_cov(dt, rank_vol_window=5, cov_window=20)


def factor_opt_47_nonlinear_volume_price_extreme_reversal_30_30_5(
    dt: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """Optimized nonlinear volume-price extreme reversal variant."""

    return factor_47_nonlinear_volume_price_extreme_reversal(
        dt,
        poly_window=30,
        kurt_window=30,
        kurt_top_window=5,
    )


def factor_opt_54_industry_fund_quality_reverse_inv(
    dt: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """Direction-adjusted industry fund-quality factor for positive long-short return."""

    return -factor_54_industry_fund_quality_reverse(dt)


def factor_55_industry_ma_value_proxy(
    dt: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """Industry-neutral moving-average spread and valuation proxy."""

    close_px = _require_field(dt, "close")
    industry = _require_field(dt, "hy")
    bbi = (
        ts_Mean(close_px, 3)
        + ts_Mean(close_px, 6)
        + ts_Mean(close_px, 12)
        + ts_Mean(close_px, 24)
    ) / 4
    ma_gap_dispersion = pn_GroupStdev(bbi - ts_EMA(close_px, 60), industry)
    price_to_3m_avg = safe_div(close_px, ts_Mean(close_px, 60)) - 1
    ev_ebitda_proxy = safe_div(_require_field(dt, "total_mv"), _require_field(dt, "ebitda"))
    return -pn_Rank(ma_gap_dispersion * Winsorize(price_to_3m_avg, 1) + ev_ebitda_proxy)


def factor_52_large_outflow_momentum_reversal(
    dt: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """Large-order outflow momentum reversal proxy."""

    turnover = _turn_rate(dt)
    sell_lg = _require_field(dt, "sell_lg_vol")
    # proxy for second-order momentum over 60 days
    second_mom = ts_Delta(ts_Delta(sell_lg, 30), 30)
    return -(turnover + second_mom)

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

FACTOR_REGISTRY.update({
    "factor_01_residual_volatility": factor_01_residual_volatility,
    "factor_02_volume_amount_efficiency": factor_02_volume_amount_efficiency,
    "factor_03_turnover_volatility_momentum": factor_03_turnover_volatility_momentum,
    "factor_04_reversal_turnover_enhanced": factor_04_reversal_turnover_enhanced,
    "factor_07_price_volume_deviation_vol": factor_07_price_volume_deviation_vol,
    "factor_09_vol_adjusted_reversal": factor_09_vol_adjusted_reversal,
    "factor_10_deviation_volume_weighted": factor_10_deviation_volume_weighted,
    "factor_11_volatility_turnover_coupling": factor_11_volatility_turnover_coupling,
    "factor_12_turnover_volatility": factor_12_turnover_volatility,
    "factor_14_main_fund_peak_reverse_rank": factor_14_main_fund_peak_reverse_rank,
    "factor_15_multi_dimensional_reversal": factor_15_multi_dimensional_reversal,
    "factor_16_price_volume_volatility_negative": factor_16_price_volume_volatility_negative,
    "factor_17_price_fund_volatility_negative": factor_17_price_fund_volatility_negative,
    "factor_18_price_volume_decay_synergy": factor_18_price_volume_decay_synergy,
    "factor_19_price_momentum_fund_volatility_reverse": factor_19_price_momentum_fund_volatility_reverse,
    "factor_20_main_flow_decay": factor_20_main_flow_decay,
    "factor_22_rank_momentum_reversal": factor_22_rank_momentum_reversal,
    "factor_23_main_flow_decay_percentage": factor_23_main_flow_decay_percentage,
    "factor_24_main_elg_flow_diff_decay": factor_24_main_elg_flow_diff_decay,
    "factor_25_main_flow_volatility_momentum": factor_25_main_flow_volatility_momentum,
    "factor_27_main_elg_flow_diff_decay": factor_27_main_elg_flow_diff_decay,
    "factor_28_main_elg_flow_synergy": factor_28_main_elg_flow_synergy,
    "factor_29_main_flow_volatility_decay": factor_29_main_flow_volatility_decay,
    "factor_30_volatility_main_flow_momentum": factor_30_volatility_main_flow_momentum,
    "factor_31_main_elg_flow_rank_diff_decay": factor_31_main_elg_flow_rank_diff_decay,
    "factor_32_momentum_flow_composite": factor_32_momentum_flow_composite,
    "factor_33_reinstatement_residual_vol_ratio": factor_33_reinstatement_residual_vol_ratio,
    "factor_34_reverse_vroc_rank_vol_cov": factor_34_reverse_vroc_rank_vol_cov,
    "factor_36_short_vol_adjusted_return": factor_36_short_vol_adjusted_return,
    "factor_37_volume_stable_close": factor_37_volume_stable_close,
    "factor_39_reverse_price_volume_rank": factor_39_reverse_price_volume_rank,
    "factor_40_fund_flow_max_drawdown": factor_40_fund_flow_max_drawdown,
    "factor_43_turnover_relative_strength_reversal": factor_43_turnover_relative_strength_reversal,
    "factor_44_volume_divergence_composite_momentum": factor_44_volume_divergence_composite_momentum,
    "factor_45_log_momentum_reverse_rank": factor_45_log_momentum_reverse_rank,
    "factor_46_price_momentum_decay_reversal": factor_46_price_momentum_decay_reversal,
    "factor_47_nonlinear_volume_price_extreme_reversal": factor_47_nonlinear_volume_price_extreme_reversal,
    "factor_48_turnover_adjusted_abnormal_price_momentum": factor_48_turnover_adjusted_abnormal_price_momentum,
    "factor_49_volatility_trend_composite": factor_49_volatility_trend_composite,
    "factor_50_reverse_standardized_decay_volume_price": factor_50_reverse_standardized_decay_volume_price,
    "factor_51_nonlinear_price_volume_flow": factor_51_nonlinear_price_volume_flow,
    "factor_52_large_outflow_momentum_reversal": factor_52_large_outflow_momentum_reversal,
    "factor_53_price_flow_cross_quantile": factor_53_price_flow_cross_quantile,
    "factor_54_industry_fund_quality_reverse": factor_54_industry_fund_quality_reverse,
    "factor_add_06_quality_x_flow": factor_add_06_quality_x_flow,
    "factor_opt_01_residual_volatility_w5": factor_opt_01_residual_volatility_w5,
    "factor_opt_01_residual_volatility_w10": factor_opt_01_residual_volatility_w10,
    "factor_opt_05_volume_price_divergence_cov_1_20": factor_opt_05_volume_price_divergence_cov_1_20,
    "factor_opt_07_price_volume_deviation_vol_w15": factor_opt_07_price_volume_deviation_vol_w15,
    "factor_opt_13_main_fund_stability_w5": factor_opt_13_main_fund_stability_w5,
    "factor_opt_33_reinstatement_residual_vol_ratio_40_20": factor_opt_33_reinstatement_residual_vol_ratio_40_20,
    "factor_opt_33_reinstatement_residual_vol_ratio_80_20": factor_opt_33_reinstatement_residual_vol_ratio_80_20,
    "factor_opt_34_reverse_vroc_rank_vol_cov_5_20": factor_opt_34_reverse_vroc_rank_vol_cov_5_20,
    "factor_opt_47_nonlinear_volume_price_extreme_reversal_30_30_5": factor_opt_47_nonlinear_volume_price_extreme_reversal_30_30_5,
    "factor_opt_54_industry_fund_quality_reverse_inv": factor_opt_54_industry_fund_quality_reverse_inv,
    "factor_55_industry_ma_value_proxy": factor_55_industry_ma_value_proxy,
})
