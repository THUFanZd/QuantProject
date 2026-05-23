"""Diagnose whether Stage 2 factors are mostly Barra-style exposures.

This script is intentionally additive: it reads the existing Stage 2 metrics,
recomputes the corresponding factor values, and writes Barra exposure
diagnostics without changing the current screening result.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FEATURE_DIR = PROJECT_ROOT / "code" / "stock1800"
for path in (PROJECT_ROOT, FEATURE_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from feature import get_ls_post, pn_TransNorm  # noqa: E402
from group_work.factor_lib import FACTOR_REGISTRY  # noqa: E402
from group_work.factor_lib.data_loader import (  # noqa: E402
    load_dt,
    load_universe_mask,
    make_listed_mask,
    read_pickle_bypass,
    resolve_data_root,
)


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

DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "group_work" / "03_factor_screening" / "stage2_outputs"


def _load_stock_codes(data_root: Path) -> list[str]:
    idxwgt_path = data_root / "idxWgt.csv"
    if not idxwgt_path.exists():
        return []
    idxwgt = pd.read_csv(idxwgt_path, index_col=0, parse_dates=True)
    return idxwgt.columns.tolist()


def _load_style_exposure(
    style_name: str,
    data_root: Path,
    like: pd.DataFrame,
    style_lag: int,
) -> pd.DataFrame:
    path = data_root / "barra" / "style" / f"{style_name}.pkl"
    if not path.exists():
        raise FileNotFoundError(f"Missing Barra style exposure: {path}")

    try:
        frame = pd.read_pickle(path)
        frame.index = pd.to_datetime(frame.index)
    except Exception:
        frame = read_pickle_bypass(path)

    stock_codes = _load_stock_codes(data_root)
    if stock_codes and len(frame.columns) <= len(stock_codes):
        frame.columns = stock_codes[: len(frame.columns)]

    frame = frame.sort_index().reindex(index=like.index, columns=like.columns)
    if style_lag:
        frame = frame.shift(style_lag)
    return pn_TransNorm(frame)


def load_style_exposures(
    data_root: Path,
    like: pd.DataFrame,
    style_lag: int,
) -> dict[str, pd.DataFrame]:
    return {
        style: _load_style_exposure(style, data_root, like, style_lag)
        for style in STYLES
    }


def _ann_sharpe(ret: pd.Series, periods: int = 252) -> float:
    std = ret.std()
    if pd.isna(std) or std == 0:
        return np.nan
    return float(ret.mean() / std * np.sqrt(periods))


def _ann_return(ret: pd.Series, periods: int = 252) -> float:
    return float(ret.mean() * periods)


def _safe_float(value: float | np.floating | None) -> float:
    if value is None or pd.isna(value):
        return np.nan
    return float(value)


def _rowwise_corr(left: pd.DataFrame, right: pd.DataFrame) -> pd.Series:
    left_values = left.to_numpy(dtype=float, copy=False)
    right_values = right.to_numpy(dtype=float, copy=False)
    mask = np.isfinite(left_values) & np.isfinite(right_values)
    n_obs = mask.sum(axis=1).astype(float)

    left_clean = np.where(mask, left_values, 0.0)
    right_clean = np.where(mask, right_values, 0.0)
    left_sum = left_clean.sum(axis=1)
    right_sum = right_clean.sum(axis=1)
    cross_sum = (left_clean * right_clean).sum(axis=1)
    left_sq_sum = (left_clean * left_clean).sum(axis=1)
    right_sq_sum = (right_clean * right_clean).sum(axis=1)

    numerator = n_obs * cross_sum - left_sum * right_sum
    left_component = n_obs * left_sq_sum - left_sum * left_sum
    right_component = n_obs * right_sq_sum - right_sum * right_sum
    denominator = np.sqrt(np.maximum(left_component * right_component, 0.0))
    corr = np.full(left_values.shape[0], np.nan)
    valid = (n_obs > 2) & (denominator > 0)
    corr[valid] = numerator[valid] / denominator[valid]
    return pd.Series(corr, index=left.index)


def _corr_stats(
    factor_stand: pd.DataFrame,
    style: pd.DataFrame,
    start_date: pd.Timestamp,
) -> tuple[pd.Series, dict[str, float]]:
    daily_corr = _rowwise_corr(factor_stand, style).loc[start_date:]
    daily_corr = daily_corr.replace([np.inf, -np.inf], np.nan).dropna()
    abs_corr = daily_corr.abs()
    stats = {
        "n_corr_days": int(daily_corr.count()),
        "corr_mean": _safe_float(daily_corr.mean()),
        "corr_abs_mean": _safe_float(abs_corr.mean()),
        "corr_abs_median": _safe_float(abs_corr.median()),
        "corr_abs_p95": _safe_float(abs_corr.quantile(0.95)) if len(abs_corr) else np.nan,
        "corr_abs_max": _safe_float(abs_corr.max()),
        "share_abs_corr_ge_030": _safe_float((abs_corr >= 0.30).mean()) if len(abs_corr) else np.nan,
        "share_abs_corr_ge_050": _safe_float((abs_corr >= 0.50).mean()) if len(abs_corr) else np.nan,
    }
    return daily_corr, stats


def _portfolio_exposure_stats(
    portfolio: pd.DataFrame,
    style: pd.DataFrame,
    start_date: pd.Timestamp,
) -> tuple[pd.Series, dict[str, float]]:
    port_values = portfolio.to_numpy(dtype=float, copy=False)
    style_values = style.to_numpy(dtype=float, copy=False)
    mask = np.isfinite(port_values) & np.isfinite(style_values)
    exposure_values = np.where(mask, port_values * style_values, 0.0).sum(axis=1)
    exposure_values[mask.sum(axis=1) == 0] = np.nan
    exposure = pd.Series(exposure_values, index=portfolio.index).loc[start_date:]
    exposure = exposure.replace([np.inf, -np.inf], np.nan).dropna()
    abs_exposure = exposure.abs()
    stats = {
        "n_exposure_days": int(exposure.count()),
        "portfolio_exposure_mean": _safe_float(exposure.mean()),
        "portfolio_exposure_abs_mean": _safe_float(abs_exposure.mean()),
        "portfolio_exposure_abs_median": _safe_float(abs_exposure.median()),
        "portfolio_exposure_abs_p95": _safe_float(abs_exposure.quantile(0.95))
        if len(abs_exposure)
        else np.nan,
        "portfolio_exposure_abs_max": _safe_float(abs_exposure.max()),
    }
    return exposure, stats


def _factor_names_from_metrics(metrics_path: Path, top: int | None) -> pd.DataFrame:
    metrics = pd.read_csv(metrics_path)
    if "factor" not in metrics.columns:
        raise ValueError(f"{metrics_path} must contain a 'factor' column")
    if top is not None:
        sort_col = "selected_sr" if "selected_sr" in metrics.columns else None
        if sort_col:
            metrics = metrics.sort_values(sort_col, ascending=False).head(top)
        else:
            metrics = metrics.head(top)
    return metrics


def evaluate_factor_barra_exposure(
    factor_name: str,
    direction: float,
    dt: dict[str, pd.DataFrame],
    listed: pd.DataFrame,
    universe_exclude: pd.DataFrame,
    styles: dict[str, pd.DataFrame],
    start_date: pd.Timestamp,
    delay: int,
    corr_threshold: float,
) -> tuple[list[dict], list[dict], dict]:
    if factor_name not in FACTOR_REGISTRY:
        raise KeyError(f"Unknown factor {factor_name!r}")

    raw_factor = FACTOR_REGISTRY[factor_name](dt)
    raw_factor = raw_factor.reindex(index=listed.index, columns=listed.columns)
    raw_factor = raw_factor.mask(universe_exclude).mask(~listed)

    factor_stand = pn_TransNorm(raw_factor) * direction
    long_w, short_w = get_ls_post(factor_stand)
    portfolio = (long_w + short_w).shift(delay)

    corr_rows: list[dict] = []
    exposure_rows: list[dict] = []
    daily_corrs: dict[str, pd.Series] = {}
    daily_exposures: dict[str, pd.Series] = {}

    for style_name, style_frame in styles.items():
        daily_corr, corr_stats = _corr_stats(factor_stand, style_frame, start_date)
        daily_exposure, exposure_stats = _portfolio_exposure_stats(
            portfolio, style_frame, start_date
        )
        corr_rows.append({"factor": factor_name, "style": style_name, **corr_stats})
        exposure_rows.append({"factor": factor_name, "style": style_name, **exposure_stats})
        daily_corrs[style_name] = daily_corr
        daily_exposures[style_name] = daily_exposure

    corr_df = pd.DataFrame(corr_rows)
    exposure_df = pd.DataFrame(exposure_rows)

    top_corr = corr_df.sort_values("corr_abs_mean", ascending=False).iloc[0]
    top_exposure = exposure_df.sort_values(
        "portfolio_exposure_abs_mean", ascending=False
    ).iloc[0]

    summary = {
        "factor": factor_name,
        "direction": direction,
        "n_days": int(corr_df["n_corr_days"].max()),
        "top_corr_style": top_corr["style"],
        "top_corr_abs_mean": _safe_float(top_corr["corr_abs_mean"]),
        "top_corr_mean": _safe_float(top_corr["corr_mean"]),
        "top_corr_abs_p95": _safe_float(top_corr["corr_abs_p95"]),
        "top_portfolio_exposure_style": top_exposure["style"],
        "top_portfolio_exposure_abs_mean": _safe_float(
            top_exposure["portfolio_exposure_abs_mean"]
        ),
        "top_portfolio_exposure_mean": _safe_float(
            top_exposure["portfolio_exposure_mean"]
        ),
        "style_proxy_flag": bool(top_corr["corr_abs_mean"] >= corr_threshold),
    }

    return corr_rows, exposure_rows, summary


def write_report(
    path: Path,
    summary: pd.DataFrame,
    corr_threshold: float,
    metrics_path: Path,
    style_lag: int,
    delay: int,
) -> None:
    ordered = summary.sort_values("top_corr_abs_mean", ascending=False)
    flagged = ordered[ordered["style_proxy_flag"]]
    try:
        metrics_display = metrics_path.resolve().relative_to(PROJECT_ROOT)
    except ValueError:
        metrics_display = metrics_path

    lines = [
        "# Stage 2 Barra Exposure Diagnostics",
        "",
        f"- Source metrics: `{metrics_display}`",
        f"- Style exposure lag: `{style_lag}` trading day(s)",
        f"- Portfolio weight delay: `{delay}` trading day(s)",
        f"- Style proxy flag: `top_corr_abs_mean >= {corr_threshold:.2f}`",
        "",
        "## What This Adds",
        "",
        "This report checks whether a Stage 2 factor is mostly a known Barra style exposure.",
        "It does not change the existing Stage 2 selection result.",
        "",
        "## Highest Style-Likeness Factors",
        "",
        "| Factor | Top style | Mean abs corr | P95 abs corr | Top portfolio style | Mean abs portfolio exposure | Flag |",
        "|---|---|---:|---:|---|---:|---|",
    ]

    for _, row in ordered.head(20).iterrows():
        lines.append(
            "| `{factor}` | {style} | {corr:.3f} | {p95:.3f} | {pstyle} | {pexp:.3f} | {flag} |".format(
                factor=row["factor"],
                style=row["top_corr_style"],
                corr=row["top_corr_abs_mean"],
                p95=row["top_corr_abs_p95"],
                pstyle=row["top_portfolio_exposure_style"],
                pexp=row["top_portfolio_exposure_abs_mean"],
                flag="yes" if row["style_proxy_flag"] else "no",
            )
        )

    lines.extend(
        [
            "",
            "## Flagged Factors",
            "",
        ]
    )

    if flagged.empty:
        lines.append("No factor crossed the configured style-proxy threshold.")
    else:
        for _, row in flagged.iterrows():
            lines.append(
                "- `{factor}` looks closest to `{style}`: mean abs corr = {corr:.3f}.".format(
                    factor=row["factor"],
                    style=row["top_corr_style"],
                    corr=row["top_corr_abs_mean"],
                )
            )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--metrics",
        type=Path,
        default=DEFAULT_OUTPUT_DIR / "factor_metrics_all.csv",
        help="Stage 2 metrics CSV containing factor names and optional directions.",
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--start-date", default="2017-01-01")
    parser.add_argument("--delay", type=int, default=2)
    parser.add_argument("--listed-days", type=int, default=20)
    parser.add_argument(
        "--style-lag",
        type=int,
        default=1,
        help="Lag Barra style exposures before comparing to factor signals.",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=10,
        help="Only analyze the top N factors by selected_sr from the metrics file.",
    )
    parser.add_argument(
        "--all-factors",
        action="store_true",
        help="Analyze every factor in the metrics file. This is slower.",
    )
    parser.add_argument(
        "--corr-threshold",
        type=float,
        default=0.30,
        help="Flag factors whose top mean absolute style correlation is at least this value.",
    )
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    top = None if args.all_factors else args.top
    metrics = _factor_names_from_metrics(args.metrics, top)
    data_root = resolve_data_root()
    dt = load_dt(["adj_close", "vol"], data_root=data_root)

    base = dt["adj_close"]
    listed = make_listed_mask(dt["vol"], listed_days=args.listed_days)
    universe_exclude = load_universe_mask(base, data_root=data_root)
    styles = load_style_exposures(data_root, base, style_lag=args.style_lag)
    start_date = pd.Timestamp(args.start_date)

    corr_rows: list[dict] = []
    exposure_rows: list[dict] = []
    summary_rows: list[dict] = []
    failures: list[dict] = []

    for _, metric_row in metrics.iterrows():
        factor_name = metric_row["factor"]
        direction = float(metric_row.get("direction", 1.0))
        print(f"Analyzing Barra exposure for {factor_name} ...", flush=True)
        try:
            factor_corr, factor_exposure, factor_summary = evaluate_factor_barra_exposure(
                factor_name=factor_name,
                direction=direction,
                dt=dt,
                listed=listed,
                universe_exclude=universe_exclude,
                styles=styles,
                start_date=start_date,
                delay=args.delay,
                corr_threshold=args.corr_threshold,
            )
        except Exception as exc:
            failures.append({"factor": factor_name, "error": repr(exc)})
            print(f"  failed: {exc!r}", flush=True)
            continue
        corr_rows.extend(factor_corr)
        exposure_rows.extend(factor_exposure)
        summary_rows.append(factor_summary)

    corr_df = pd.DataFrame(corr_rows)
    exposure_df = pd.DataFrame(exposure_rows)
    summary_df = pd.DataFrame(summary_rows)

    corr_path = args.output_dir / "barra_factor_style_corr.csv"
    exposure_path = args.output_dir / "barra_portfolio_style_exposure.csv"
    summary_path = args.output_dir / "barra_exposure_summary.csv"
    report_path = args.output_dir / "barra_exposure_report.md"
    failures_path = args.output_dir / "barra_exposure_failures.json"

    corr_df.to_csv(corr_path, index=False, encoding="utf-8-sig")
    exposure_df.to_csv(exposure_path, index=False, encoding="utf-8-sig")
    summary_df.to_csv(summary_path, index=False, encoding="utf-8-sig")
    write_report(
        report_path,
        summary_df,
        corr_threshold=args.corr_threshold,
        metrics_path=args.metrics,
        style_lag=args.style_lag,
        delay=args.delay,
    )

    if failures:
        failures_path.write_text(
            json.dumps(failures, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    elif failures_path.exists():
        failures_path.unlink()

    print(
        json.dumps(
            {
                "data_root": str(data_root),
                "analyzed": int(len(summary_df)),
                "failures": failures,
                "outputs": {
                    "summary": str(summary_path),
                    "factor_style_corr": str(corr_path),
                    "portfolio_style_exposure": str(exposure_path),
                    "report": str(report_path),
                },
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
