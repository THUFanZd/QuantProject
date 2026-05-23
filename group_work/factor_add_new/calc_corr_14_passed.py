"""Compute the 14x14 correlation table for AR/SR-qualified factors."""

from __future__ import annotations

import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
WORKSPACE_ROOT = PROJECT_ROOT.parent
FEATURE_DIR = PROJECT_ROOT / "code" / "stock1800"
CURRENT_DIR = Path(__file__).resolve().parent
for path in (PROJECT_ROOT, FEATURE_DIR, CURRENT_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from feature import pn_TransNorm  # noqa: E402
from group_work.factor_lib import factors as factor_module  # noqa: E402
from group_work.factor_lib.data_loader import load_dt, load_universe_mask, make_listed_mask  # noqa: E402
from group_work.factor_lib.factors import FACTOR_REGISTRY  # noqa: E402
from factor_add_2_recalc import FACTOR_ADD_2_RECALC_REGISTRY  # noqa: E402


OUTPUT_DIR = CURRENT_DIR / "outputs"


def resolve_course_data_root() -> Path:
    candidates = [
        PROJECT_ROOT / "data" / "stock1000_px",
        PROJECT_ROOT / "data_1800" / "stock1000" / "data",
        WORKSPACE_ROOT / "课程资料（中证1000）" / "stock1000" / "data",
    ]
    for candidate in candidates:
        if (candidate / "matrix").exists():
            return candidate
    for candidate in WORKSPACE_ROOT.glob("*1000*/stock1000/data"):
        if (candidate / "matrix").exists():
            return candidate
    raise FileNotFoundError("Cannot find a course data root with a matrix folder.")


def patch_factor_data_root(data_root: Path) -> None:
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
    return float(left.corrwith(right, axis=1).mean())


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    data_root = resolve_course_data_root()
    patch_factor_data_root(data_root)

    fields = [
        "adj_close",
        "open",
        "high",
        "close",
        "amount",
        "vol",
        "totalRet",
        "turnover_rate",
        "float_share",
        "pb",
        "total_mv",
        "hy",
        "net_mf_amount",
        "buy_elg_amount",
        "sell_elg_amount",
    ]
    dt = load_dt(fields, data_root=data_root)
    listed = make_listed_mask(dt["vol"], listed_days=20)
    mask = load_universe_mask(dt["close"], data_root=data_root)

    factor_specs = [
        ("factor_add_06_quality_x_flow", lambda: FACTOR_REGISTRY["factor_add_06_quality_x_flow"](dt)),
        ("factor_opt_01_residual_volatility_w5", lambda: FACTOR_REGISTRY["factor_opt_01_residual_volatility_w5"](dt)),
        ("factor_opt_01_residual_volatility_w10", lambda: FACTOR_REGISTRY["factor_opt_01_residual_volatility_w10"](dt)),
        ("factor_opt_05_volume_price_divergence_cov_1_20", lambda: FACTOR_REGISTRY["factor_opt_05_volume_price_divergence_cov_1_20"](dt)),
        ("factor_opt_07_price_volume_deviation_vol_w15", lambda: FACTOR_REGISTRY["factor_opt_07_price_volume_deviation_vol_w15"](dt)),
        ("factor_opt_13_main_fund_stability_w5", lambda: FACTOR_REGISTRY["factor_opt_13_main_fund_stability_w5"](dt)),
        ("factor_opt_33_reinstatement_residual_vol_ratio_40_20", lambda: FACTOR_REGISTRY["factor_opt_33_reinstatement_residual_vol_ratio_40_20"](dt)),
        ("factor_opt_33_reinstatement_residual_vol_ratio_80_20", lambda: FACTOR_REGISTRY["factor_opt_33_reinstatement_residual_vol_ratio_80_20"](dt)),
        ("factor_opt_34_reverse_vroc_rank_vol_cov_5_20", lambda: FACTOR_REGISTRY["factor_opt_34_reverse_vroc_rank_vol_cov_5_20"](dt)),
        ("factor_opt_47_nonlinear_volume_price_extreme_reversal_30_30_5", lambda: FACTOR_REGISTRY["factor_opt_47_nonlinear_volume_price_extreme_reversal_30_30_5"](dt)),
        ("factor_opt_54_industry_fund_quality_reverse_inv", lambda: FACTOR_REGISTRY["factor_opt_54_industry_fund_quality_reverse_inv"](dt)),
        ("factor_add2_adj_05_f34_15_25_industry", lambda: FACTOR_ADD_2_RECALC_REGISTRY["factor_add2_adj_05_f34_15_25_industry"](dt)),
        ("factor_add2_adj_07_f18_decay30_industry", lambda: FACTOR_ADD_2_RECALC_REGISTRY["factor_add2_adj_07_f18_decay30_industry"](dt)),
        ("factor_add2_adj_04_f34_10_30_industry", lambda: FACTOR_ADD_2_RECALC_REGISTRY["factor_add2_adj_04_f34_10_30_industry"](dt)),
    ]

    scores = {}
    for factor_name, fn in factor_specs:
        print(f"Scoring {factor_name}", flush=True)
        scores[factor_name] = score(fn(), mask, listed)

    names = [factor_name for factor_name, _ in factor_specs]
    corr = pd.DataFrame(index=names, columns=names, dtype=float)
    for i, left in enumerate(names):
        for j, right in enumerate(names):
            corr.loc[left, right] = 1.0 if i == j else mean_xs_corr(scores[left], scores[right])

    abs_corr = corr.abs()
    pair_rows = []
    for i, left in enumerate(names):
        for right in names[i + 1 :]:
            pair_rows.append(
                {
                    "factor_a": left,
                    "factor_b": right,
                    "corr": corr.loc[left, right],
                    "abs_corr": abs_corr.loc[left, right],
                }
            )
    pairs = pd.DataFrame(pair_rows).sort_values("abs_corr", ascending=False)

    corr_path = OUTPUT_DIR / "corr_14_passed_factors.csv"
    abs_corr_path = OUTPUT_DIR / "abs_corr_14_passed_factors.csv"
    pairs_path = OUTPUT_DIR / "corr_pairs_14_passed_factors.csv"
    corr.to_csv(corr_path, encoding="utf-8-sig")
    abs_corr.to_csv(abs_corr_path, encoding="utf-8-sig")
    pairs.to_csv(pairs_path, index=False, encoding="utf-8-sig")

    payload = {
        "data_root": str(data_root),
        "corr_csv": str(corr_path),
        "abs_corr_csv": str(abs_corr_path),
        "pairs_csv": str(pairs_path),
        "top_abs_pairs": pairs.head(10).to_dict(orient="records"),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
