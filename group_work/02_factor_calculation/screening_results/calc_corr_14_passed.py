"""Compute correlations among AR/SR-qualified stage-2 factors."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]
FEATURE_DIR = PROJECT_ROOT / "code" / "stock1800"
CURRENT_DIR = Path(__file__).resolve().parent
for path in (PROJECT_ROOT, FEATURE_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from feature import pn_TransNorm  # noqa: E402
from group_work.factor_lib import factors as factor_module  # noqa: E402
from group_work.factor_lib.data_loader import (  # noqa: E402
    load_dt,
    load_universe_mask,
    make_listed_mask,
    resolve_data_root,
)
from group_work.factor_lib.factors import FACTOR_REGISTRY  # noqa: E402


FACTOR_KEYS = [
    "factor_add_06_quality_x_flow",
    "factor_opt_01_residual_volatility_w5",
    "factor_opt_01_residual_volatility_w10",
    "factor_opt_05_volume_price_divergence_cov_1_20",
    "factor_opt_07_price_volume_deviation_vol_w15",
    "factor_opt_13_main_fund_stability_w5",
    "factor_opt_33_reinstatement_residual_vol_ratio_40_20",
    "factor_opt_33_reinstatement_residual_vol_ratio_80_20",
    "factor_opt_34_reverse_vroc_rank_vol_cov_5_20",
    "factor_opt_47_nonlinear_volume_price_extreme_reversal_30_30_5",
    "factor_opt_54_industry_fund_quality_reverse_inv",
    "factor_add2_adj_05_f34_15_25_industry",
    "factor_add2_adj_07_f18_decay30_industry",
    "factor_add2_adj_04_f34_10_30_industry",
    "factor_add3_amihud_illiq_10_industry",
    "factor_add3_gap_down_3",
    "factor_add3_intraday_hml_vol_120_industry_inv",
    "factor_add3_overnight_reversal_3_industry_inv",
    "factor_add3_turnover_weighted_reversal_20_industry",
    "factor_add3_f18_decay90_industry",
]


def patch_factor_data_root(data_root: Path) -> None:
    """Point lazy factor-field loading at the same data root used by the loader."""

    factor_module.COURSE_DATA_DIR = data_root
    factor_module.MATRIX_DIR = data_root / "matrix"
    factor_module.FIN_MATRIX_DIR = data_root / "finMatrix"
    for name in ("_stock_codes", "_load_local_field_cached"):
        fn = getattr(factor_module, name, None)
        if hasattr(fn, "cache_clear"):
            fn.cache_clear()


def score(raw: pd.DataFrame, mask: pd.DataFrame, listed: pd.DataFrame) -> pd.DataFrame:
    raw = raw.replace([np.inf, -np.inf], np.nan).mask(mask).mask(~listed)
    return pn_TransNorm(raw).replace([np.inf, -np.inf], np.nan)


def mean_xs_corr(left: pd.DataFrame, right: pd.DataFrame) -> float:
    left_values = left.to_numpy(dtype=float)
    right_values = right.to_numpy(dtype=float)
    valid = np.isfinite(left_values) & np.isfinite(right_values)
    counts = valid.sum(axis=1)

    left_sum = np.where(valid, left_values, 0.0).sum(axis=1)
    right_sum = np.where(valid, right_values, 0.0).sum(axis=1)
    left_mean = np.divide(left_sum, counts, out=np.full_like(left_sum, np.nan), where=counts > 0)
    right_mean = np.divide(right_sum, counts, out=np.full_like(right_sum, np.nan), where=counts > 0)

    left_centered = np.where(valid, left_values - left_mean[:, None], 0.0)
    right_centered = np.where(valid, right_values - right_mean[:, None], 0.0)
    covariance = (left_centered * right_centered).sum(axis=1)
    denom = np.sqrt((left_centered * left_centered).sum(axis=1) * (right_centered * right_centered).sum(axis=1))
    daily_corr = np.divide(covariance, denom, out=np.full_like(covariance, np.nan), where=(counts > 1) & (denom > 0))
    return float(np.nanmean(daily_corr))


def build_pair_table(corr: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for i, left in enumerate(corr.index):
        for right in corr.index[i + 1 :]:
            value = corr.loc[left, right]
            rows.append(
                {
                    "factor_a": left,
                    "factor_b": right,
                    "corr": value,
                    "abs_corr": abs(value),
                }
            )
    return pd.DataFrame(rows).sort_values("abs_corr", ascending=False)


def find_max_low_corr_sets(
    corr: pd.DataFrame,
    threshold: float,
    max_sets: int = 20,
) -> list[tuple[str, ...]]:
    """Find largest factor subsets where every pair has abs(corr) below threshold."""

    names = list(corr.index)
    adjacency = {
        name: {
            other
            for other in names
            if other != name and abs(corr.loc[name, other]) < threshold
        }
        for name in names
    }
    best: list[tuple[str, ...]] = []
    best_size = 0

    def expand(current: list[str], candidates: set[str]) -> None:
        nonlocal best, best_size
        if len(current) + len(candidates) < best_size:
            return
        if not candidates:
            current_tuple = tuple(current)
            if len(current_tuple) > best_size:
                best_size = len(current_tuple)
                best = [current_tuple]
            elif len(current_tuple) == best_size and len(best) < max_sets:
                best.append(current_tuple)
            return

        while candidates:
            if len(current) + len(candidates) < best_size:
                return
            vertex = max(candidates, key=lambda item: len(adjacency[item] & candidates))
            candidates.remove(vertex)
            expand(current + [vertex], candidates & adjacency[vertex])

    expand([], set(names))
    return best


def calculate_correlations(
    factor_keys: list[str],
    listed_days: int,
    cache_dir: Path | None,
    refresh_cache: bool,
) -> tuple[pd.DataFrame, pd.DataFrame, Path]:
    missing = [key for key in factor_keys if key not in FACTOR_REGISTRY]
    if missing:
        raise KeyError(f"Missing factor keys from FACTOR_REGISTRY: {missing}")

    data_root = resolve_data_root()
    patch_factor_data_root(data_root)
    dt = load_dt(["adj_close", "open", "high", "close", "amount", "vol", "totalRet"], data_root=data_root)
    listed = make_listed_mask(dt["vol"], listed_days=listed_days)
    mask = load_universe_mask(dt["close"], data_root=data_root)

    if cache_dir is not None:
        cache_dir.mkdir(parents=True, exist_ok=True)

    scores = {}
    for factor_name in factor_keys:
        cache_path = cache_dir / f"{factor_name}.pkl" if cache_dir is not None else None
        if cache_path is not None and cache_path.exists() and not refresh_cache:
            print(f"Loading cached score {factor_name}", flush=True)
            scores[factor_name] = pd.read_pickle(cache_path)
            continue

        print(f"Scoring {factor_name}", flush=True)
        raw = FACTOR_REGISTRY[factor_name](dt)
        scores[factor_name] = score(raw, mask, listed)
        if cache_path is not None:
            tmp_path = cache_path.with_suffix(".tmp")
            scores[factor_name].to_pickle(tmp_path)
            tmp_path.replace(cache_path)

    corr = pd.DataFrame(index=factor_keys, columns=factor_keys, dtype=float)
    for i, left in enumerate(factor_keys):
        for j, right in enumerate(factor_keys):
            corr.loc[left, right] = 1.0 if i == j else mean_xs_corr(scores[left], scores[right])
    return corr, build_pair_table(corr), data_root


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--listed-days", type=int, default=20)
    parser.add_argument("--threshold", type=float, default=0.3)
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=PROJECT_ROOT / "archive" / "root_scratch" / "corr14_score_cache",
        help="Directory for reusable standardized factor-score caches.",
    )
    parser.add_argument("--refresh-cache", action="store_true")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=CURRENT_DIR,
        help="Directory for correlation CSV outputs.",
    )
    args = parser.parse_args()

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    corr, pairs, data_root = calculate_correlations(
        FACTOR_KEYS,
        listed_days=args.listed_days,
        cache_dir=args.cache_dir,
        refresh_cache=args.refresh_cache,
    )
    abs_corr = corr.abs()

    output_stem = f"{len(FACTOR_KEYS)}_passed_factors"
    corr_path = output_dir / f"corr_{output_stem}.csv"
    abs_corr_path = output_dir / f"abs_corr_{output_stem}.csv"
    pairs_path = output_dir / f"corr_pairs_{output_stem}.csv"
    corr.to_csv(corr_path, encoding="utf-8-sig")
    abs_corr.to_csv(abs_corr_path, encoding="utf-8-sig")
    pairs.to_csv(pairs_path, index=False, encoding="utf-8-sig")

    max_low_corr_sets = find_max_low_corr_sets(corr, args.threshold)
    max_sets_path = output_dir / f"max_low_corr_sets_{output_stem}.csv"
    pd.DataFrame(
        [
            {"set_size": len(factor_set), "factors": ";".join(factor_set)}
            for factor_set in max_low_corr_sets
        ]
    ).to_csv(max_sets_path, index=False, encoding="utf-8-sig")

    payload = {
        "data_root": str(data_root),
        "factor_count": len(FACTOR_KEYS),
        "pair_count": len(pairs),
        "low_abs_corr_pair_count": int((pairs["abs_corr"] < args.threshold).sum()),
        "threshold": args.threshold,
        "max_low_corr_set_size": len(max_low_corr_sets[0]) if max_low_corr_sets else 0,
        "max_low_corr_set_count_shown": len(max_low_corr_sets),
        "max_low_corr_sets_csv": str(max_sets_path),
        "max_low_corr_sets": [list(factor_set) for factor_set in max_low_corr_sets[:5]],
        "cache_dir": str(args.cache_dir) if args.cache_dir is not None else "",
        "corr_csv": str(corr_path),
        "abs_corr_csv": str(abs_corr_path),
        "pairs_csv": str(pairs_path),
        "top_abs_pairs": pairs.head(10).to_dict(orient="records"),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
