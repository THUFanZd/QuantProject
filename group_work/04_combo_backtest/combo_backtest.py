"""Stage 4 composite-factor construction and Barra-neutral backtest.

This script consumes the ten Stage-3 selected factors, combines them with a
historical IC-based weighting rule, neutralizes the composite score against
Barra style and industry exposures, and forms an index-enhanced long-only
portfolio.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
STAGE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = STAGE_DIR / "outputs"
INPUT_DIR = STAGE_DIR / "inputs"
FEATURE_DIR = PROJECT_ROOT / "code" / "stock1800"

DEFAULT_DATA_ROOT = Path(os.environ.get("TS_DAILY_DATA_ROOT", r"C:/ts_daily/stock1000/data"))
SELECTED_FACTORS_PATH = INPUT_DIR / "selected_factors.csv"
FACTOR_QUALITY_PATH = INPUT_DIR / "factor_quality_summary.csv"

for path in (PROJECT_ROOT, FEATURE_DIR, STAGE_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from feature import get_ls_post, pn_TransNorm  # noqa: E402
from group_work.factor_lib.factors import FACTOR_REGISTRY  # noqa: E402
from barra_support import (  # noqa: E402
    STYLES,
    industry_label,
    load_data,
    mean_cross_sectional_corr,
    patch_factor_data_root,
    read_idxwgt,
    regress_one_factor,
    score_factor,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build and backtest the Stage-4 composite factor.")
    parser.add_argument("--data-root", type=Path, default=DEFAULT_DATA_ROOT)
    parser.add_argument("--start-date", default="2017-01-01")
    parser.add_argument("--delay", type=int, default=2, help="Signal-to-trade delay in trading days.")
    parser.add_argument(
        "--weight-method",
        choices=("equal", "ic", "ic_ir"),
        default="ic_ir",
        help="Factor combination method; IC methods use only historically observable IC values.",
    )
    parser.add_argument(
        "--weight-window",
        type=int,
        default=252,
        help="Trailing observable-IC window for dynamic IC/IC_IR weights; pass 0 for expanding history.",
    )
    parser.add_argument(
        "--min-weight-history",
        type=int,
        default=252,
        help="Minimum historically observable IC observations before the active portfolio starts.",
    )
    parser.add_argument(
        "--active-budget",
        type=float,
        default=0.20,
        help="Maximum gross active overlay relative to the CSI1000 benchmark.",
    )
    parser.add_argument(
        "--cost-rate",
        type=float,
        default=0.0,
        help="One-way transaction cost rate applied to enhanced-portfolio turnover.",
    )
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    return parser.parse_args()


def load_selection_and_metrics() -> tuple[pd.DataFrame, pd.DataFrame]:
    selected = pd.read_csv(SELECTED_FACTORS_PATH)
    quality = pd.read_csv(FACTOR_QUALITY_PATH)
    missing = sorted(set(selected["factor_key"]) - set(quality["factor"]))
    if missing:
        raise KeyError(f"Missing Stage-2 quality metrics for selected factors: {missing}")
    return selected, quality


def summarize_factor_weights(
    selected: pd.DataFrame,
    quality: pd.DataFrame,
    weight_history: pd.DataFrame,
    method: str,
) -> pd.DataFrame:
    table = selected.merge(
        quality[["factor", "stage2_ar", "stage2_sr", "stage2_ic_mean", "stage2_ic_ir"]],
        left_on="factor_key",
        right_on="factor",
        how="left",
    ).drop(columns="factor")

    live = weight_history.loc[weight_history.abs().sum(axis=1) > 0]
    if live.empty:
        raise ValueError("No live factor weights were produced; reduce --min-weight-history or inspect IC data.")
    table["weight_method"] = method
    table["latest_combo_weight"] = table["factor_key"].map(live.iloc[-1])
    table["mean_combo_weight"] = table["factor_key"].map(live.mean(axis=0))
    table["mean_abs_combo_weight"] = table["factor_key"].map(live.abs().mean(axis=0))
    return table


def build_standardized_factors(
    selected: pd.DataFrame,
    dt: dict[str, pd.DataFrame],
    universe_mask: pd.DataFrame,
    listed: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    frames: dict[str, pd.DataFrame] = {}
    for factor_key in selected["factor_key"]:
        if factor_key not in FACTOR_REGISTRY:
            raise KeyError(f"Selected factor is not registered: {factor_key}")
        print(f"Scoring factor: {factor_key}", flush=True)
        raw = FACTOR_REGISTRY[factor_key](dt)
        frames[factor_key] = score_factor(raw, universe_mask, listed)
    return frames


def build_historical_factor_weights(
    scores: dict[str, pd.DataFrame],
    total_ret: pd.DataFrame,
    method: str,
    delay: int,
    window: int,
    min_history: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if min_history <= 0:
        raise ValueError("--min-weight-history must be positive.")
    if window < 0 or (window > 0 and min_history > window):
        raise ValueError("--weight-window must be 0 or at least --min-weight-history.")

    reference = next(iter(scores.values()))
    factor_keys = list(scores)
    if method == "equal":
        weights = pd.DataFrame(1.0 / len(factor_keys), index=reference.index, columns=factor_keys)
        return weights, pd.DataFrame(index=reference.index, columns=factor_keys, dtype=float)

    forward_ret = total_ret.reindex(index=reference.index, columns=reference.columns).shift(-delay)
    observable_ic = pd.DataFrame(
        {
            factor_key: score.corrwith(forward_ret, axis=1).shift(delay)
            for factor_key, score in scores.items()
        },
        index=reference.index,
    )
    history = (
        observable_ic.rolling(window=window, min_periods=min_history)
        if window > 0
        else observable_ic.expanding(min_periods=min_history)
    )
    raw_weight = history.mean()
    if method == "ic_ir":
        raw_weight = raw_weight.div(history.std().replace(0.0, np.nan))

    denominator = raw_weight.abs().sum(axis=1).replace(0.0, np.nan)
    weights = raw_weight.div(denominator, axis=0).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    return weights, observable_ic


def combine_factor_scores(
    scores: dict[str, pd.DataFrame],
    weight_history: pd.DataFrame,
) -> pd.DataFrame:
    reference = next(iter(scores.values()))
    numerator = pd.DataFrame(0.0, index=reference.index, columns=reference.columns)
    valid_weight = pd.DataFrame(0.0, index=reference.index, columns=reference.columns)

    for factor_key, frame in scores.items():
        weight = weight_history[factor_key].reindex(reference.index)
        numerator = numerator.add(frame.fillna(0.0).mul(weight, axis=0), fill_value=0.0)
        valid_weight = valid_weight.add(frame.notna().astype(float).mul(weight.abs(), axis=0), fill_value=0.0)

    combo = numerator.div(valid_weight.replace(0.0, np.nan))
    return pn_TransNorm(combo).replace([np.inf, -np.inf], np.nan)


def barra_neutralize(
    combo: pd.DataFrame,
    dt: dict[str, pd.DataFrame],
    styles: dict[str, pd.DataFrame],
) -> tuple[pd.DataFrame, dict[str, pd.DataFrame], pd.DataFrame, pd.Series, pd.Series, pd.Series]:
    industry = dt["hy"].reindex(index=combo.index, columns=combo.columns)
    industry_codes = sorted(
        int(code)
        for code in pd.unique(industry.to_numpy().ravel())
        if pd.notna(code) and int(code) != 0
    )
    shifted_styles = {
        style: styles[style].shift(1).reindex(index=combo.index, columns=combo.columns)
        for style in STYLES
    }
    residual, r2, alpha, nobs = regress_one_factor(combo, shifted_styles, industry, industry_codes)
    return residual, shifted_styles, industry, r2, alpha, nobs


def normalize_benchmark_weights(idxwgt: pd.DataFrame, like: pd.DataFrame) -> pd.DataFrame:
    weights = idxwgt.reindex(index=like.index, columns=like.columns).fillna(0.0)
    row_sum = weights.sum(axis=1).replace(0.0, np.nan)
    return weights.div(row_sum, axis=0).fillna(0.0)


def build_enhanced_portfolio(
    benchmark_w: pd.DataFrame,
    active_w: pd.DataFrame,
    active_budget: float,
) -> tuple[pd.DataFrame, pd.Series]:
    if active_budget < 0:
        raise ValueError("--active-budget must be non-negative.")

    short_leg = active_w.where(active_w < 0)
    feasible_scale = benchmark_w.div(-short_leg).min(axis=1, skipna=True) * 0.999
    feasible_scale = feasible_scale.replace([np.inf, -np.inf], np.nan).fillna(active_budget).clip(lower=0.0)
    scale = feasible_scale.clip(upper=active_budget)

    portfolio_w = benchmark_w.add(active_w.mul(scale, axis=0), fill_value=0.0)
    portfolio_w = portfolio_w.clip(lower=0.0)
    portfolio_w = portfolio_w.div(portfolio_w.sum(axis=1).replace(0.0, np.nan), axis=0).fillna(0.0)
    return portfolio_w, scale


def calculate_returns(
    portfolio_w: pd.DataFrame,
    benchmark_w: pd.DataFrame,
    active_w: pd.DataFrame,
    total_ret: pd.DataFrame,
    active_scale: pd.Series,
    delay: int,
    cost_rate: float,
    start_date: str,
) -> pd.DataFrame:
    returns = pd.DataFrame(index=portfolio_w.index)
    aligned_ret = total_ret.reindex(index=portfolio_w.index, columns=portfolio_w.columns)

    enhanced_turnover = portfolio_w.diff().abs().sum(axis=1) / 2.0
    active_turnover = active_w.diff().abs().sum(axis=1) / 2.0
    returns["portfolio_ret_gross"] = (portfolio_w.shift(delay) * aligned_ret).sum(axis=1, min_count=1)
    returns["benchmark_ret"] = (benchmark_w.shift(delay) * aligned_ret).sum(axis=1, min_count=1)
    returns["neutral_ls_ret"] = (active_w.shift(delay) * aligned_ret).sum(axis=1, min_count=1)
    returns["portfolio_turnover"] = enhanced_turnover.shift(delay)
    returns["neutral_ls_turnover"] = active_turnover.shift(delay)
    returns["active_scale"] = active_scale.shift(delay)
    returns["transaction_cost"] = returns["portfolio_turnover"].fillna(0.0) * cost_rate
    returns["portfolio_ret"] = returns["portfolio_ret_gross"] - returns["transaction_cost"]
    returns["excess_ret"] = returns["portfolio_ret"] - returns["benchmark_ret"]
    returns = returns.loc[returns.index >= pd.Timestamp(start_date)].dropna(
        subset=["portfolio_ret", "benchmark_ret", "excess_ret"]
    )

    returns["portfolio_nav"] = (1.0 + returns["portfolio_ret"]).cumprod()
    returns["benchmark_nav"] = (1.0 + returns["benchmark_ret"]).cumprod()
    returns["excess_nav"] = (1.0 + returns["excess_ret"]).cumprod()
    returns["neutral_ls_nav"] = (1.0 + returns["neutral_ls_ret"].fillna(0.0)).cumprod()
    return returns


def annual_return(ret: pd.Series) -> float:
    return float(ret.mean() * 252)


def annual_sharpe(ret: pd.Series) -> float:
    std = ret.std()
    if not np.isfinite(std) or std == 0:
        return np.nan
    return float(ret.mean() / std * np.sqrt(252))


def max_drawdown(nav: pd.Series) -> float:
    return float((nav / nav.cummax() - 1.0).min())


def build_monthly_returns(returns: pd.DataFrame) -> pd.DataFrame:
    columns = ["portfolio_ret", "benchmark_ret", "excess_ret", "neutral_ls_ret"]
    monthly = (1.0 + returns[columns]).resample("ME").prod(min_count=1) - 1.0
    monthly["excess_win"] = monthly["excess_ret"] > 0
    return monthly


def build_exposure_outputs(
    combo: pd.DataFrame,
    neutral_combo: pd.DataFrame,
    active_w: pd.DataFrame,
    shifted_styles: dict[str, pd.DataFrame],
    industry: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    style_rows: list[dict[str, float | str]] = []
    for style in STYLES:
        active_exposure = (active_w * shifted_styles[style]).sum(axis=1, min_count=1)
        style_rows.append(
            {
                "style": style,
                "pre_neutral_signal_corr": mean_cross_sectional_corr(combo, shifted_styles[style]),
                "post_neutral_signal_corr": mean_cross_sectional_corr(neutral_combo, shifted_styles[style]),
                "mean_active_exposure": float(active_exposure.mean(skipna=True)),
                "max_abs_active_exposure": float(active_exposure.abs().max(skipna=True)),
            }
        )

    industry_codes = sorted(
        int(code)
        for code in pd.unique(industry.to_numpy().ravel())
        if pd.notna(code) and int(code) != 0
    )
    industry_signal_rows: list[dict[str, float | str]] = []
    for code in industry_codes:
        pre = combo.where(industry == code).mean(axis=1, skipna=True).mean(skipna=True)
        post = neutral_combo.where(industry == code).mean(axis=1, skipna=True).mean(skipna=True)
        industry_signal_rows.append(
            {
                "industry": industry_label(code),
                "pre_neutral_signal_mean": float(pre),
                "post_neutral_signal_mean": float(post),
            }
        )

    industry_active_exposure = pd.DataFrame(
        {
            industry_label(code): active_w.where(industry == code, 0.0).sum(axis=1)
            for code in industry_codes
        }
    )
    return pd.DataFrame(style_rows), pd.DataFrame(industry_signal_rows), industry_active_exposure


def build_metrics(
    returns: pd.DataFrame,
    monthly_returns: pd.DataFrame,
    style_exposure: pd.DataFrame,
    industry_signal_exposure: pd.DataFrame,
    industry_active_exposure: pd.DataFrame,
    r2: pd.Series,
    args: argparse.Namespace,
) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "weight_method": args.weight_method,
                "start_date": returns.index.min().date().isoformat(),
                "end_date": returns.index.max().date().isoformat(),
                "delay": args.delay,
                "cost_rate": args.cost_rate,
                "target_active_budget": args.active_budget,
                "mean_realized_active_scale": returns["active_scale"].mean(),
                "portfolio_annual_return": annual_return(returns["portfolio_ret"]),
                "benchmark_annual_return": annual_return(returns["benchmark_ret"]),
                "annual_excess_return": annual_return(returns["excess_ret"]),
                "excess_sharpe": annual_sharpe(returns["excess_ret"]),
                "excess_max_drawdown": max_drawdown(returns["excess_nav"]),
                "excess_positive_month_count": int(monthly_returns["excess_win"].sum()),
                "excess_month_count": int(monthly_returns["excess_win"].count()),
                "excess_monthly_win_rate": float(monthly_returns["excess_win"].mean()),
                "neutral_ls_annual_return": annual_return(returns["neutral_ls_ret"]),
                "neutral_ls_sharpe": annual_sharpe(returns["neutral_ls_ret"]),
                "neutral_ls_max_drawdown": max_drawdown(returns["neutral_ls_nav"]),
                "combo_mean_barra_r2": r2.mean(skipna=True),
                "max_post_neutral_style_corr": style_exposure["post_neutral_signal_corr"].abs().max(),
                "max_mean_active_style_exposure": style_exposure["mean_active_exposure"].abs().max(),
                "pre_industry_signal_dispersion": industry_signal_exposure["pre_neutral_signal_mean"].std(),
                "post_neutral_industry_signal_dispersion": industry_signal_exposure["post_neutral_signal_mean"].std(),
                "max_post_neutral_industry_signal_exposure": industry_signal_exposure[
                    "post_neutral_signal_mean"
                ].abs().max(),
                "max_mean_active_industry_exposure": industry_active_exposure.mean(axis=0).abs().max(),
            }
        ]
    )


def save_latest_holdings(
    portfolio_w: pd.DataFrame,
    benchmark_w: pd.DataFrame,
    active_w: pd.DataFrame,
    active_scale: pd.Series,
    output_path: Path,
) -> None:
    date = portfolio_w.index.max()
    latest = pd.DataFrame(
        {
            "stock": portfolio_w.columns,
            "benchmark_weight": benchmark_w.loc[date].to_numpy(),
            "unit_active_weight": active_w.loc[date].to_numpy(),
            "realized_active_weight": active_w.loc[date].to_numpy() * float(active_scale.loc[date]),
            "portfolio_weight": portfolio_w.loc[date].to_numpy(),
        }
    )
    latest = latest.loc[latest["portfolio_weight"] > 0].sort_values("portfolio_weight", ascending=False)
    latest.insert(0, "date", date.date().isoformat())
    latest.to_csv(output_path, index=False, encoding="utf-8-sig")


def plot_outputs(returns: pd.DataFrame, output_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.plot(returns.index, returns["portfolio_nav"], label="Composite portfolio", linewidth=1.7)
    ax.plot(returns.index, returns["benchmark_nav"], label="CSI 1000 benchmark", linewidth=1.4)
    ax.set_title("Stage 4 Portfolio NAV vs CSI 1000")
    ax.set_ylabel("NAV")
    ax.legend()
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(output_dir / "combo_nav_vs_benchmark.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.plot(returns.index, returns["excess_nav"], label="Long-only excess NAV", linewidth=1.7)
    ax.plot(returns.index, returns["neutral_ls_nav"], label="Neutral long-short NAV", linewidth=1.3)
    ax.axhline(1.0, color="gray", linestyle="--", linewidth=0.8)
    ax.set_title("Stage 4 Excess and Neutral Long-Short NAV")
    ax.set_ylabel("NAV")
    ax.legend()
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(output_dir / "combo_excess_nav.png", dpi=180)
    plt.close(fig)


def markdown_table(frame: pd.DataFrame) -> str:
    columns = list(frame.columns)
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for row in frame.itertuples(index=False, name=None):
        lines.append("| " + " | ".join(str(value) for value in row) + " |")
    return "\n".join(lines)


def write_report(
    metrics: pd.DataFrame,
    weights: pd.DataFrame,
    style_exposure: pd.DataFrame,
    industry_signal_exposure: pd.DataFrame,
    output_dir: Path,
    args: argparse.Namespace,
) -> None:
    row = metrics.iloc[0]
    weight_show = weights[["factor_key", "stage2_ic_ir", "latest_combo_weight", "mean_abs_combo_weight"]].copy()
    weight_show["stage2_ic_ir"] = weight_show["stage2_ic_ir"].map(lambda x: f"{x:.4f}")
    weight_show["latest_combo_weight"] = weight_show["latest_combo_weight"].map(lambda x: f"{x:.2%}")
    weight_show["mean_abs_combo_weight"] = weight_show["mean_abs_combo_weight"].map(lambda x: f"{x:.2%}")
    exposure_show = style_exposure[["style", "pre_neutral_signal_corr", "post_neutral_signal_corr"]].copy()
    for column in exposure_show.columns[1:]:
        exposure_show[column] = exposure_show[column].map(lambda x: f"{x:.4f}")
    industry_show = industry_signal_exposure.copy()
    industry_show["sort_key"] = industry_show["pre_neutral_signal_mean"].abs()
    industry_show = industry_show.sort_values("sort_key", ascending=False).head(10).drop(columns="sort_key")
    for column in industry_show.columns[1:]:
        industry_show[column] = industry_show[column].map(lambda x: f"{x:.4f}")

    report = f"""# 第四阶段：组合因子构建与回测

## 实现口径

- 入选因子：`inputs/selected_factors.csv` 中冻结的 10 个低相关达标因子。
- 合成方法：滚动历史 `{args.weight_method.upper()}` 加权；主结果默认使用 `IC_IR` 加权。
- 防前视权重：每个信号日仅使用当日已实现且可观测的历史 IC，滚动窗口 `{args.weight_window}` 个交易日、最少 `{args.min_weight_history}` 个观测；不读取未来时期的因子表现决定当期权重。
- 中性化：逐日截面回归剔除 10 个 Barra 风格暴露和申万一级行业哑变量，主动信号取回归残差。
- 持仓：以中证1000 `idxWgt` 为基准，叠加中性主动权重；主动覆盖比例上限为 `{args.active_budget:.2%}`，并动态收缩以确保最终持仓非负且权重和为 1。
- 回测：信号与收益间延迟 `{args.delay}` 个交易日，风格暴露使用上一交易日数据，单边成本率 `{args.cost_rate:.4%}`。

## 组合权重

{markdown_table(weight_show)}

## 回测结果

| 指标 | 结果 |
| --- | ---: |
| 回测区间 | {row["start_date"]} 至 {row["end_date"]} |
| 组合年化收益 | {row["portfolio_annual_return"]:.2%} |
| 中证1000年化收益 | {row["benchmark_annual_return"]:.2%} |
| 年化超额收益 | {row["annual_excess_return"]:.2%} |
| 超额 Sharpe | {row["excess_sharpe"]:.3f} |
| 超额最大回撤 | {row["excess_max_drawdown"]:.2%} |
| 超额月度胜率 | {row["excess_monthly_win_rate"]:.2%}（{int(row["excess_positive_month_count"])}/{int(row["excess_month_count"])}） |
| 中性多空年化收益 | {row["neutral_ls_annual_return"]:.2%} |
| 中性多空 Sharpe | {row["neutral_ls_sharpe"]:.3f} |

## 中性化检查

组合信号在中性化前后的 Barra 风格截面相关均值如下。中性化后残差用于构建主动持仓。

{markdown_table(exposure_show)}

行业均值暴露离散度由 `{row["pre_industry_signal_dispersion"]:.4f}` 降至 `{row["post_neutral_industry_signal_dispersion"]:.4f}`。以下展示中性化前绝对暴露最大的 10 个行业：

{markdown_table(industry_show)}

## 输出文件

- `combo_factor_weights.csv`：10 个因子及其组合权重。
- `combo_metrics.csv`：回测核心指标。
- `combo_daily_returns.csv`：日收益和净值序列。
- `combo_monthly_returns.csv`：月度收益和超额胜负记录。
- `combo_style_exposure.csv`：组合中性化前后的风格暴露。
- `combo_industry_signal_exposure.csv`：组合中性化前后的行业暴露对比。
- `combo_industry_active_exposure.csv`：中性主动组合每日行业权重偏离。
- `combo_factor_weights_timeseries.csv`：严格历史口径下每日组合权重。
- `combo_observable_ic_timeseries.csv`：权重估计可使用的历史 IC 序列。
- `combo_latest_holdings.csv`：末日实际持仓。
- `combo_nav_vs_benchmark.png`：组合与中证1000净值对比。
- `combo_excess_nav.png`：超额收益与中性多空净值曲线。
"""
    (output_dir / "combo_backtest_report_zh.md").write_text(report, encoding="utf-8")


def main() -> None:
    args = parse_args()
    if not args.data_root.exists():
        raise FileNotFoundError(
            f"Data root does not exist: {args.data_root}. Pass --data-root or set TS_DAILY_DATA_ROOT."
        )
    args.output_dir.mkdir(parents=True, exist_ok=True)

    patch_factor_data_root(args.data_root)
    selected, quality = load_selection_and_metrics()

    print(f"Loading data from {args.data_root}", flush=True)
    dt, listed, universe_mask, styles = load_data(args.data_root)
    scores = build_standardized_factors(selected, dt, universe_mask, listed)
    weight_history, observable_ic = build_historical_factor_weights(
        scores,
        dt["totalRet"],
        args.weight_method,
        args.delay,
        args.weight_window,
        args.min_weight_history,
    )
    weight_table = summarize_factor_weights(selected, quality, weight_history, args.weight_method)
    combo = combine_factor_scores(scores, weight_history)
    neutral_combo, shifted_styles, industry, r2, alpha, nobs = barra_neutralize(combo, dt, styles)

    long_w, short_w = get_ls_post(neutral_combo)
    active_w = long_w + short_w
    idxwgt = read_idxwgt(args.data_root)
    benchmark_w = normalize_benchmark_weights(idxwgt, active_w)
    portfolio_w, active_scale = build_enhanced_portfolio(benchmark_w, active_w, args.active_budget)
    live_signal_dates = weight_history.index[weight_history.abs().sum(axis=1) > 0]
    if live_signal_dates.empty:
        raise ValueError("No live active-signal dates after historical weight estimation.")
    first_signal_position = portfolio_w.index.get_loc(live_signal_dates.min())
    first_trade_position = min(first_signal_position + args.delay, len(portfolio_w.index) - 1)
    effective_start_date = max(pd.Timestamp(args.start_date), portfolio_w.index[first_trade_position]).date().isoformat()

    returns = calculate_returns(
        portfolio_w,
        benchmark_w,
        active_w,
        dt["totalRet"],
        active_scale,
        args.delay,
        args.cost_rate,
        effective_start_date,
    )
    monthly_returns = build_monthly_returns(returns)
    style_exposure, industry_signal_exposure, industry_active_exposure = build_exposure_outputs(
        combo, neutral_combo, active_w, shifted_styles, industry
    )
    metrics = build_metrics(
        returns, monthly_returns, style_exposure, industry_signal_exposure, industry_active_exposure, r2, args
    )
    regression_diagnostics = pd.DataFrame({"r2": r2, "alpha": alpha, "nobs": nobs})

    weight_table.to_csv(args.output_dir / "combo_factor_weights.csv", index=False, encoding="utf-8-sig")
    metrics.to_csv(args.output_dir / "combo_metrics.csv", index=False, encoding="utf-8-sig")
    returns.to_csv(args.output_dir / "combo_daily_returns.csv", encoding="utf-8-sig")
    monthly_returns.to_csv(args.output_dir / "combo_monthly_returns.csv", encoding="utf-8-sig")
    weight_history.to_csv(args.output_dir / "combo_factor_weights_timeseries.csv", encoding="utf-8-sig")
    observable_ic.to_csv(args.output_dir / "combo_observable_ic_timeseries.csv", encoding="utf-8-sig")
    style_exposure.to_csv(args.output_dir / "combo_style_exposure.csv", index=False, encoding="utf-8-sig")
    industry_signal_exposure.to_csv(args.output_dir / "combo_industry_signal_exposure.csv", index=False, encoding="utf-8-sig")
    industry_active_exposure.to_csv(args.output_dir / "combo_industry_active_exposure.csv", encoding="utf-8-sig")
    regression_diagnostics.to_csv(args.output_dir / "combo_regression_diagnostics.csv", encoding="utf-8-sig")
    save_latest_holdings(
        portfolio_w, benchmark_w, active_w, active_scale, args.output_dir / "combo_latest_holdings.csv"
    )
    plot_outputs(returns, args.output_dir)
    write_report(metrics, weight_table, style_exposure, industry_signal_exposure, args.output_dir, args)

    print(metrics.to_string(index=False), flush=True)
    print(f"Stage-4 outputs saved to {args.output_dir}", flush=True)


if __name__ == "__main__":
    main()
