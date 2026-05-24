"""Stage 3 Barra style and industry exposure analysis.

Regenerates the third-stage deliverables from the recovered local data
environment at C:/ts_daily/stock1000/data.
"""

from __future__ import annotations

import math
import os
import pickletools
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.rcParams["font.sans-serif"] = [
    "Microsoft YaHei",
    "SimHei",
    "SimSun",
    "Arial Unicode MS",
    "DejaVu Sans",
]
plt.rcParams["axes.unicode_minus"] = False


PROJECT_ROOT = Path(__file__).resolve().parents[2]
STAGE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = STAGE_DIR / "outputs"
DATA_ROOT = Path(os.environ.get("TS_DAILY_DATA_ROOT", r"C:/ts_daily/stock1000/data"))
FEATURE_DIR = PROJECT_ROOT / "code" / "stock1800"

START_DATE = pd.Timestamp("2017-01-01")
LOAD_START = pd.Timestamp("2015-01-01")
STYLE_THRESHOLD = 0.40
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
from group_work.factor_lib.factors import FACTOR_REGISTRY  # noqa: E402


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
    """Assign course-trading dates/stock codes and subset to the work window."""

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
    """Read old int64 matrix pickle files such as hy.pkl."""

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
    """Read Barra style matrices saved in stock-major order."""

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


def load_selected_factors() -> pd.DataFrame:
    return pd.read_csv(STAGE_DIR / "selected_factors.csv")


def read_stage2_metrics(factor_key: str) -> dict[str, float]:
    metrics_path = PROJECT_ROOT / "group_work" / "02_factor_calculation" / "outputs" / "sign_weight" / f"{factor_key}_metrics.csv"
    if not metrics_path.exists():
        return {}
    row = pd.read_csv(metrics_path).iloc[0]
    return {
        "stage2_ar": float(row.get("ls_ar", np.nan)),
        "stage2_sr": float(row.get("ls_sr", np.nan)),
        "stage2_ic_mean": float(row.get("ic_mean", np.nan)),
        "stage2_ic_ir": float(row.get("ic_ir", np.nan)),
        "stage2_latest_coverage": float(row.get("latest_coverage", np.nan)),
    }


def score_factor(raw: pd.DataFrame, universe_mask: pd.DataFrame, listed: pd.DataFrame) -> pd.DataFrame:
    factor = raw.replace([np.inf, -np.inf], np.nan)
    factor = factor.mask(universe_mask).mask(~listed)
    factor = pn_TransNorm(factor).replace([np.inf, -np.inf], np.nan)
    return factor.loc[factor.index >= START_DATE]


def mean_cross_sectional_corr(left: pd.DataFrame, right: pd.DataFrame) -> float:
    corr = left.corrwith(right, axis=1)
    return float(corr.mean(skipna=True))


def industry_mean_exposure(factor: pd.DataFrame, industry: pd.DataFrame, industry_codes: list[int]) -> pd.Series:
    return pd.Series(
        {
            industry_label(code): float(factor.where(industry == code).mean(axis=1, skipna=True).mean(skipna=True))
            for code in industry_codes
        }
    )


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
        styles = np.column_stack([arr[i, valid] for arr in style_arrays])
        labels = ind[valid]
        dummies = (labels[:, None] == dummy_codes[None, :]).astype(float)
        x = np.column_stack([np.ones(len(yv)), styles, dummies])

        try:
            beta, *_ = np.linalg.lstsq(x, yv, rcond=None)
        except np.linalg.LinAlgError:
            continue

        fitted = x @ beta
        eps = yv - fitted
        tss = float(np.sum((yv - yv.mean()) ** 2))
        if tss > 0:
            r2_value = 1.0 - float(np.sum(eps ** 2)) / tss
            # A few near-degenerate cross-sections can be numerically unstable.
            # For explanatory power reporting, keep R2 inside its natural range.
            r2.loc[date] = min(1.0, max(0.0, r2_value))
        alpha.loc[date] = float(beta[0])
        nobs.loc[date] = float(len(yv))
        residual.iloc[i, np.flatnonzero(valid)] = eps

    return residual, r2, alpha, nobs


def exposure_text(row: pd.Series) -> str:
    hits = [(style, float(row[style])) for style in STYLES if pd.notna(row[style]) and abs(float(row[style])) > STYLE_THRESHOLD]
    if not hits:
        return "无显著单一风格暴露(|corr|<=0.4)"
    hits.sort(key=lambda item: abs(item[1]), reverse=True)
    return "; ".join(f"{style}{'+' if value > 0 else '-'}{abs(value):.2f}" for style, value in hits)


def alpha_class(pure_alpha_ratio: float) -> str:
    if not math.isfinite(pure_alpha_ratio):
        return "样本不足"
    if pure_alpha_ratio >= 0.70:
        return "Alpha主导"
    if pure_alpha_ratio >= 0.40:
        return "Alpha/风格混合"
    return "风格或行业驱动"


def plot_heatmap(
    data: pd.DataFrame,
    path: Path,
    title: str,
    cmap: str = "RdBu_r",
    symmetric: bool = True,
    annotate: bool = False,
) -> None:
    values = data.to_numpy(dtype=float)
    if symmetric:
        vmax = max(float(np.nanmax(np.abs(values))), 1e-6)
        vmin = -vmax
    else:
        vmin = float(np.nanmin(values))
        vmax = float(np.nanmax(values))
        if vmin == vmax:
            vmax = vmin + 1e-6

    fig_w = max(10.0, 0.52 * len(data.columns))
    fig_h = max(6.5, 0.36 * len(data.index))
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    im = ax.imshow(values, aspect="auto", cmap=cmap, vmin=vmin, vmax=vmax)
    ax.set_title(title, fontsize=12)
    ax.set_xticks(np.arange(len(data.columns)))
    ax.set_xticklabels(data.columns, rotation=45, ha="right", fontsize=8)
    ax.set_yticks(np.arange(len(data.index)))
    ax.set_yticklabels(data.index, fontsize=7)
    if annotate and data.shape[0] <= 12 and data.shape[1] <= 12:
        for i in range(data.shape[0]):
            for j in range(data.shape[1]):
                value = values[i, j]
                if np.isfinite(value):
                    ax.text(j, i, f"{value:.2f}", ha="center", va="center", fontsize=6, color="black")
    fig.colorbar(im, ax=ax, fraction=0.028, pad=0.02)
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def md_table(df: pd.DataFrame, max_rows: int | None = None) -> str:
    show = df if max_rows is None else df.head(max_rows)
    columns = list(show.columns)
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for _, row in show.iterrows():
        vals = []
        for col in columns:
            value = row[col]
            if isinstance(value, (float, np.floating)):
                vals.append("" if pd.isna(value) else f"{float(value):.4f}")
            else:
                vals.append(str(value))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def write_report(
    factor_quality: pd.DataFrame,
    main_exposures: pd.DataFrame,
    style_matrix: pd.DataFrame,
    regression_summary: pd.DataFrame,
    neutral_compare: pd.DataFrame,
    industry_summary: pd.DataFrame,
) -> None:
    style_preview = style_matrix.round(4).reset_index().rename(columns={"index": "factor"})
    regression_preview = regression_summary[
        ["factor", "mean_r2", "pure_alpha_ratio", "alpha_class", "main_style_exposure"]
    ].sort_values("mean_r2", ascending=False)
    neutral_preview = neutral_compare[
        [
            "factor",
            "pre_max_abs_style_corr",
            "post_max_abs_style_corr",
            "pre_industry_dispersion",
            "post_industry_dispersion",
        ]
    ].sort_values("pre_max_abs_style_corr", ascending=False)

    report = f"""# 第三阶段 Barra 风格暴露分析报告

## 分析口径

- 数据环境：`{DATA_ROOT}`
- 分析区间：`{START_DATE.date()}` 至 `{style_matrix.attrs.get("end_date", "")}`
- 股票池：中证1000成分股，使用 `idxWgt.csv` 屏蔽非成分股，并要求上市满20个交易日
- 因子处理：原始因子 -> 股票池/上市天数过滤 -> `pn_TransNorm` 截面标准化
- 风格暴露：10个 Barra CNE5 风格因子，使用 `shift(1)` 避免前视偏差
- 行业暴露：使用 `hy.pkl` 的申万2021一级行业编码，映射为中文行业名称后计算各行业内因子均值
- Barra 回归：逐日截面回归 `factor = alpha + 10 styles + industry dummies + residual`

## 10个有效因子及第二阶段表现

{md_table(factor_quality[["factor", "stage2_ar", "stage2_sr", "stage2_ic_mean", "stage2_ic_ir", "latest_coverage"]], max_rows=20)}

## 10因子 x 10风格暴露矩阵

矩阵元素为 2017 年以来逐日截面相关系数的时间均值。

{md_table(style_preview, max_rows=20)}

## 主要风格暴露说明

阈值设为 `|corr| > {STYLE_THRESHOLD}`。

{md_table(main_exposures, max_rows=20)}

## Barra 纯 Alpha 比例

`mean_r2` 越高，说明因子越容易被 Barra 风格和行业解释；`pure_alpha_ratio = 1 - mean_r2` 越高，说明纯 Alpha 成分越强。

{md_table(regression_preview, max_rows=20)}

## 行业暴露摘要

`industry_dispersion` 为各行业平均暴露的标准差，用来衡量行业偏离强弱。

{md_table(industry_summary, max_rows=20)}

## 中性化前后对比

这里的中性化因子取 Barra 回归残差。若 `post_max_abs_style_corr` 和 `post_industry_dispersion` 明显下降，说明 Barra 风格和行业暴露得到了有效压制。

{md_table(neutral_preview, max_rows=20)}

## 结论

本阶段产出显示，10个有效因子整体可以进一步拆分为 Alpha 主导、Alpha/风格混合、以及风格或行业驱动三类。后续第四阶段构建组合因子时，建议优先使用 Barra 回归残差或至少对组合因子进行行业和风格中性化，以降低 Size、Liquidity、ResVol 等常见风险因子的重复暴露。

## 输出文件

- `style_exposure_matrix.csv` / `style_exposure_heatmap.png`
- `main_style_exposures.csv`
- `industry_code_map.csv`
- `industry_exposure_matrix.csv` / `industry_exposure_heatmap.png`
- `barra_regression_summary.csv`
- `neutralization_compare.csv`
- `style_exposure_matrix_neutralized.csv` / `style_exposure_heatmap_neutralized.png`
- `industry_exposure_matrix_neutralized.csv` / `industry_exposure_heatmap_neutralized.png`
- `barra_regression_r2_timeseries.csv`
- `barra_regression_alpha_timeseries.csv`
- `barra_regression_nobs_timeseries.csv`
"""
    (OUTPUT_DIR / "barra_exposure_report_zh.md").write_text(report, encoding="utf-8")
    (OUTPUT_DIR / "barra_exposure_report.md").write_text(report, encoding="utf-8")


def main() -> None:
    if not DATA_ROOT.exists():
        raise FileNotFoundError(f"Data root does not exist: {DATA_ROOT}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    patch_factor_data_root(DATA_ROOT)

    print(f"Loading data from {DATA_ROOT} ...", flush=True)
    dt, listed, universe_mask, styles = load_data(DATA_ROOT)
    selected = load_selected_factors()

    analysis_index = dt["close"].index[dt["close"].index >= START_DATE]
    industry = dt["hy"].reindex(index=analysis_index, columns=dt["close"].columns)
    industry_codes = sorted(
        int(x)
        for x in pd.unique(industry.to_numpy().ravel())
        if pd.notna(x) and int(x) != 0
    )
    shifted_styles = {
        style: styles[style].shift(1).reindex(index=analysis_index, columns=dt["close"].columns)
        for style in STYLES
    }

    factor_frames: dict[str, pd.DataFrame] = {}
    quality_rows: list[dict[str, object]] = []
    style_matrix = pd.DataFrame(index=selected["factor_key"], columns=STYLES, dtype=float)
    industry_columns = [industry_label(code) for code in industry_codes]
    industry_matrix = pd.DataFrame(index=selected["factor_key"], columns=industry_columns, dtype=float)

    for row in selected.itertuples(index=False):
        factor_key = row.factor_key
        if factor_key not in FACTOR_REGISTRY:
            raise KeyError(f"Unknown factor in FACTOR_REGISTRY: {factor_key}")
        print(f"Computing factor: {factor_key}", flush=True)

        raw = FACTOR_REGISTRY[factor_key](dt)
        factor = score_factor(raw, universe_mask, listed)
        factor = factor.reindex(index=analysis_index, columns=dt["close"].columns)
        factor_frames[factor_key] = factor

        for style in STYLES:
            style_matrix.loc[factor_key, style] = mean_cross_sectional_corr(factor, shifted_styles[style])
        industry_matrix.loc[factor_key] = industry_mean_exposure(factor, industry, industry_codes)

        metrics = read_stage2_metrics(factor_key)
        quality_rows.append(
            {
                "factor": factor_key,
                "display_name": row.display_name,
                "selection_bucket": row.selection_bucket,
                "notes": row.notes,
                "latest_coverage": float(factor.iloc[-1].notna().mean()),
                **metrics,
            }
        )

    print("Running Barra style + industry regressions ...", flush=True)
    neutral_style_matrix = pd.DataFrame(index=style_matrix.index, columns=STYLES, dtype=float)
    neutral_industry_matrix = pd.DataFrame(index=industry_matrix.index, columns=industry_matrix.columns, dtype=float)
    r2_ts = pd.DataFrame(index=analysis_index)
    alpha_ts = pd.DataFrame(index=analysis_index)
    nobs_ts = pd.DataFrame(index=analysis_index)
    regression_rows: list[dict[str, object]] = []
    neutral_rows: list[dict[str, object]] = []

    for factor_key, factor in factor_frames.items():
        print(f"Regressing factor: {factor_key}", flush=True)
        residual, r2, alpha, nobs = regress_one_factor(factor, shifted_styles, industry, industry_codes)
        r2_ts[factor_key] = r2
        alpha_ts[factor_key] = alpha
        nobs_ts[factor_key] = nobs

        for style in STYLES:
            neutral_style_matrix.loc[factor_key, style] = mean_cross_sectional_corr(residual, shifted_styles[style])
        neutral_industry_matrix.loc[factor_key] = industry_mean_exposure(residual, industry, industry_codes)

        mean_r2 = float(r2.mean(skipna=True))
        pure_alpha_ratio = 1.0 - mean_r2 if math.isfinite(mean_r2) else np.nan
        regression_rows.append(
            {
                "factor": factor_key,
                "mean_r2": mean_r2,
                "median_r2": float(r2.median(skipna=True)),
                "pure_alpha_ratio": pure_alpha_ratio,
                "mean_alpha": float(alpha.mean(skipna=True)),
                "mean_nobs": float(nobs.replace(0, np.nan).mean(skipna=True)),
                "alpha_class": alpha_class(pure_alpha_ratio),
                "main_style_exposure": exposure_text(style_matrix.loc[factor_key]),
            }
        )
        neutral_rows.append(
            {
                "factor": factor_key,
                "pre_max_abs_style_corr": float(style_matrix.loc[factor_key].abs().max()),
                "post_max_abs_style_corr": float(neutral_style_matrix.loc[factor_key].abs().max()),
                "pre_mean_abs_style_corr": float(style_matrix.loc[factor_key].abs().mean()),
                "post_mean_abs_style_corr": float(neutral_style_matrix.loc[factor_key].abs().mean()),
                "pre_industry_dispersion": float(industry_matrix.loc[factor_key].astype(float).std()),
                "post_industry_dispersion": float(neutral_industry_matrix.loc[factor_key].astype(float).std()),
                "mean_r2": mean_r2,
                "pure_alpha_ratio": pure_alpha_ratio,
            }
        )

    factor_quality = pd.DataFrame(quality_rows)
    factor_quality = factor_quality.rename(
        columns={
            "stage2_ar": "stage2_ar",
            "stage2_sr": "stage2_sr",
            "stage2_ic_mean": "stage2_ic_mean",
            "stage2_ic_ir": "stage2_ic_ir",
        }
    )
    factor_quality["stage2_ar"] = factor_quality["stage2_ar"].astype(float)
    factor_quality["stage2_sr"] = factor_quality["stage2_sr"].astype(float)
    factor_quality["stage2_ic_mean"] = factor_quality["stage2_ic_mean"].astype(float)
    factor_quality["stage2_ic_ir"] = factor_quality["stage2_ic_ir"].astype(float)
    factor_quality["latest_coverage"] = factor_quality["latest_coverage"].astype(float)

    main_exposures = pd.DataFrame(
        {
            "factor": style_matrix.index,
            "main_style_exposure": [exposure_text(style_matrix.loc[factor]) for factor in style_matrix.index],
            "max_abs_style_corr": style_matrix.abs().max(axis=1).to_numpy(dtype=float),
        }
    )
    regression_summary = pd.DataFrame(regression_rows).sort_values("mean_r2", ascending=False)
    neutral_compare = pd.DataFrame(neutral_rows)
    industry_summary = pd.DataFrame(
        {
            "factor": industry_matrix.index,
            "industry_dispersion": industry_matrix.astype(float).std(axis=1).to_numpy(dtype=float),
            "top_abs_industry": [
                str(industry_matrix.loc[factor].astype(float).abs().idxmax())
                for factor in industry_matrix.index
            ],
            "top_abs_industry_exposure": [
                float(industry_matrix.loc[factor].astype(float).loc[industry_matrix.loc[factor].astype(float).abs().idxmax()])
                for factor in industry_matrix.index
            ],
        }
    ).sort_values("industry_dispersion", ascending=False)

    style_matrix.attrs["end_date"] = str(analysis_index.max().date())

    print("Writing Stage 3 outputs ...", flush=True)
    industry_code_map = pd.DataFrame(
        {
            "industry_code": industry_codes,
            "industry_name": [SW2021_L1_INDUSTRY_MAP.get(code, "未知行业") for code in industry_codes],
            "industry_label": [industry_label(code) for code in industry_codes],
        }
    )
    selected.to_csv(OUTPUT_DIR / "selected_factors_used.csv", index=False, encoding="utf-8-sig")
    industry_code_map.to_csv(OUTPUT_DIR / "industry_code_map.csv", index=False, encoding="utf-8-sig")
    factor_quality.to_csv(OUTPUT_DIR / "factor_quality_summary.csv", index=False, encoding="utf-8-sig")
    style_matrix.to_csv(OUTPUT_DIR / "style_exposure_matrix.csv", encoding="utf-8-sig")
    neutral_style_matrix.to_csv(OUTPUT_DIR / "style_exposure_matrix_neutralized.csv", encoding="utf-8-sig")
    industry_matrix.to_csv(OUTPUT_DIR / "industry_exposure_matrix.csv", encoding="utf-8-sig")
    neutral_industry_matrix.to_csv(OUTPUT_DIR / "industry_exposure_matrix_neutralized.csv", encoding="utf-8-sig")
    main_exposures.to_csv(OUTPUT_DIR / "main_style_exposures.csv", index=False, encoding="utf-8-sig")
    regression_summary.to_csv(OUTPUT_DIR / "barra_regression_summary.csv", index=False, encoding="utf-8-sig")
    neutral_compare.to_csv(OUTPUT_DIR / "neutralization_compare.csv", index=False, encoding="utf-8-sig")
    industry_summary.to_csv(OUTPUT_DIR / "industry_exposure_summary.csv", index=False, encoding="utf-8-sig")
    r2_ts.to_csv(OUTPUT_DIR / "barra_regression_r2_timeseries.csv", encoding="utf-8-sig")
    alpha_ts.to_csv(OUTPUT_DIR / "barra_regression_alpha_timeseries.csv", encoding="utf-8-sig")
    nobs_ts.to_csv(OUTPUT_DIR / "barra_regression_nobs_timeseries.csv", encoding="utf-8-sig")

    plot_heatmap(style_matrix, OUTPUT_DIR / "style_exposure_heatmap.png", "Factor vs Barra Style Exposure", annotate=True)
    plot_heatmap(
        neutral_style_matrix,
        OUTPUT_DIR / "style_exposure_heatmap_neutralized.png",
        "Neutralized Factor vs Barra Style Exposure",
        annotate=True,
    )
    plot_heatmap(industry_matrix, OUTPUT_DIR / "industry_exposure_heatmap.png", "Factor Industry Mean Exposure")
    plot_heatmap(
        neutral_industry_matrix,
        OUTPUT_DIR / "industry_exposure_heatmap_neutralized.png",
        "Neutralized Factor Industry Mean Exposure",
    )

    write_report(factor_quality, main_exposures, style_matrix, regression_summary, neutral_compare, industry_summary)
    print(f"Done. Outputs saved to {OUTPUT_DIR}", flush=True)


if __name__ == "__main__":
    main()
