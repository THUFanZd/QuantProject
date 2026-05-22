"""Correlation table for 8 passing single factors plus 5 passing composites."""

from __future__ import annotations

from itertools import combinations
from pathlib import Path
import sys

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FEATURE_DIR = PROJECT_ROOT / "code" / "stock1800"
for path in (PROJECT_ROOT, FEATURE_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from feature import pn_TransNorm  # noqa: E402
from group_work.factor_lib import factors as factor_module  # noqa: E402
from group_work.factor_lib.factors import FACTOR_REGISTRY  # noqa: E402
from group_work.factor_lib.data_loader import (  # noqa: E402
    load_dt,
    load_universe_mask,
    make_listed_mask,
    resolve_data_root as original_resolve_data_root,
)


OUTPUT_DIR = PROJECT_ROOT / "group_work" / "02_factor_calculation" / "outputs_corr_try1"
CACHE_DIR = OUTPUT_DIR / "cache"


COMPONENTS = {
    "factor_01_default": {
        "factor": "factor_01_residual_volatility",
        "params": {},
        "direction": 1,
    },
    "factor_07_default": {
        "factor": "factor_07_price_volume_deviation_vol",
        "params": {},
        "direction": 1,
    },
    "factor_33_default": {
        "factor": "factor_33_reinstatement_residual_vol_ratio",
        "params": {},
        "direction": 1,
    },
    "factor_54_default_reversed": {
        "factor": "factor_54_industry_fund_quality_reverse",
        "params": {},
        "direction": -1,
    },
    "factor_05_opt": {
        "factor": "factor_05_volume_price_divergence_cov",
        "params": {"delta_window": 1, "cov_window": 20},
        "direction": 1,
    },
    "factor_13_opt": {
        "factor": "factor_13_main_fund_stability",
        "params": {"window": 5},
        "direction": 1,
    },
    "factor_34_opt": {
        "factor": "factor_34_reverse_vroc_rank_vol_cov",
        "params": {"rank_vol_window": 5, "cov_window": 20},
        "direction": 1,
    },
    "factor_47_opt": {
        "factor": "factor_47_nonlinear_volume_price_extreme_reversal",
        "params": {"poly_window": 30, "kurt_window": 30, "kurt_top_window": 5},
        "direction": 1,
    },
    "factor_47_default": {
        "factor": "factor_47_nonlinear_volume_price_extreme_reversal",
        "params": {},
        "direction": 1,
    },
}

TARGET_FACTORS = [
    "factor_01_default",
    "factor_07_default",
    "factor_33_default",
    "factor_54_default_reversed",
    "factor_05_opt",
    "factor_13_opt",
    "factor_34_opt",
    "factor_47_opt",
    "cmp_09_low_corr",
    "cmp_04_reversal_extreme",
    "cmp_02_volume_price",
    "cmp_10_orth_47_to_05",
    "cmp_08_multiscale_47",
]


def resolve_data_root() -> Path:
    try:
        return original_resolve_data_root()
    except FileNotFoundError:
        for parent in [PROJECT_ROOT, *PROJECT_ROOT.parents]:
            try:
                for child in parent.iterdir():
                    candidate = child / "stock1000" / "data"
                    if (candidate / "matrix").exists():
                        return candidate
            except OSError:
                continue
    raise FileNotFoundError("Could not find stock1000 data root.")


def patch_factor_data_root(data_root: Path) -> None:
    factor_module.COURSE_DATA_DIR = data_root
    factor_module.MATRIX_DIR = data_root / "matrix"
    factor_module.FIN_MATRIX_DIR = data_root / "finMatrix"
    for name in ("_stock_codes", "_load_local_field_cached"):
        fn = getattr(factor_module, name, None)
        if hasattr(fn, "cache_clear"):
            fn.cache_clear()


def clean_factor(factor: pd.DataFrame, mask: pd.DataFrame, listed: pd.DataFrame) -> pd.DataFrame:
    factor = factor.replace([np.inf, -np.inf], np.nan)
    return factor.mask(mask).mask(~listed)


def score_component(
    name: str,
    dt: dict[str, pd.DataFrame],
    universe_mask: pd.DataFrame,
    listed: pd.DataFrame,
) -> pd.DataFrame:
    cache_path = CACHE_DIR / f"{name}.pkl"
    if cache_path.exists():
        return pd.read_pickle(cache_path)

    spec = COMPONENTS[name]
    fn = FACTOR_REGISTRY[spec["factor"]]
    raw = clean_factor(fn(dt, **spec["params"]), universe_mask, listed)
    score = pn_TransNorm(raw).replace([np.inf, -np.inf], np.nan) * spec["direction"]
    score.to_pickle(cache_path)
    return score


def mean_score(scores: dict[str, pd.DataFrame], names: list[str]) -> pd.DataFrame:
    stacked = [scores[name].stack(dropna=False) for name in names]
    return pd.concat(stacked, axis=1).mean(axis=1).unstack()


def orthogonalize_by_date(y: pd.DataFrame, x: pd.DataFrame) -> pd.DataFrame:
    y_centered = y.sub(y.mean(axis=1), axis=0)
    x_centered = x.sub(x.mean(axis=1), axis=0)
    cov = (x_centered * y_centered).mean(axis=1)
    var = (x_centered * x_centered).mean(axis=1)
    beta = cov / var.replace(0, np.nan)
    return y_centered.sub(x_centered.mul(beta, axis=0), axis=0)


def final_score(factor: pd.DataFrame) -> pd.DataFrame:
    return pn_TransNorm(factor).replace([np.inf, -np.inf], np.nan)


def daily_cross_section_corr(a: pd.DataFrame, b: pd.DataFrame) -> float:
    return float(a.corrwith(b, axis=1).mean())


def find_largest_low_corr_subset(corr_abs: pd.DataFrame, threshold: float = 0.3) -> tuple[list[str], float]:
    names = list(corr_abs.index)
    for k in range(len(names), 0, -1):
        best_subset: list[str] | None = None
        best_max_corr = np.inf
        for combo in combinations(names, k):
            sub = corr_abs.loc[list(combo), list(combo)]
            vals = sub.where(np.triu(np.ones(sub.shape), k=1).astype(bool)).stack()
            max_corr = float(vals.max()) if len(vals) else 0.0
            if max_corr < threshold and max_corr < best_max_corr:
                best_subset = list(combo)
                best_max_corr = max_corr
        if best_subset is not None:
            return best_subset, best_max_corr
    return [], np.nan


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    data_root = resolve_data_root()
    patch_factor_data_root(data_root)
    dt = load_dt(["adj_close", "open", "high", "close", "amount", "vol", "totalRet"], data_root=data_root)
    listed = make_listed_mask(dt["vol"], listed_days=20)
    universe_mask = load_universe_mask(dt["close"], data_root=data_root)

    scores: dict[str, pd.DataFrame] = {}
    for name in COMPONENTS:
        print(f"Scoring {name}", flush=True)
        scores[name] = score_component(name, dt, universe_mask, listed)

    factors = {
        "factor_01_default": final_score(scores["factor_01_default"]),
        "factor_07_default": final_score(scores["factor_07_default"]),
        "factor_33_default": final_score(scores["factor_33_default"]),
        "factor_54_default_reversed": final_score(scores["factor_54_default_reversed"]),
        "factor_05_opt": final_score(scores["factor_05_opt"]),
        "factor_13_opt": final_score(scores["factor_13_opt"]),
        "factor_34_opt": final_score(scores["factor_34_opt"]),
        "factor_47_opt": final_score(scores["factor_47_opt"]),
        "cmp_09_low_corr": final_score(
            mean_score(scores, ["factor_33_default", "factor_54_default_reversed", "factor_05_opt", "factor_34_opt"])
        ),
        "cmp_04_reversal_extreme": final_score(
            mean_score(scores, ["factor_34_opt", "factor_47_opt", "factor_54_default_reversed"])
        ),
        "cmp_02_volume_price": final_score(mean_score(scores, ["factor_05_opt", "factor_47_opt"])),
        "cmp_10_orth_47_to_05": final_score(
            mean_score(
                {
                    "factor_05_opt": scores["factor_05_opt"],
                    "orth_47": orthogonalize_by_date(scores["factor_47_opt"], scores["factor_05_opt"]),
                },
                ["factor_05_opt", "orth_47"],
            )
        ),
        "cmp_08_multiscale_47": final_score(mean_score(scores, ["factor_47_default", "factor_47_opt"])),
    }

    corr = pd.DataFrame(index=TARGET_FACTORS, columns=TARGET_FACTORS, dtype=float)
    for left in TARGET_FACTORS:
        for right in TARGET_FACTORS:
            corr.loc[left, right] = 1.0 if left == right else daily_cross_section_corr(factors[left], factors[right])

    corr_abs = corr.abs()
    subset, max_abs_corr = find_largest_low_corr_subset(corr_abs, threshold=0.3)
    pair_rows = []
    for left, right in combinations(TARGET_FACTORS, 2):
        pair_rows.append(
            {
                "factor_a": left,
                "factor_b": right,
                "corr": corr.loc[left, right],
                "abs_corr": corr_abs.loc[left, right],
                "over_0_3": bool(corr_abs.loc[left, right] >= 0.3),
            }
        )
    pairs = pd.DataFrame(pair_rows).sort_values("abs_corr", ascending=False)

    corr.to_csv(OUTPUT_DIR / "factor_corr_13_try1.csv", encoding="utf-8-sig")
    corr_abs.to_csv(OUTPUT_DIR / "factor_abs_corr_13_try1.csv", encoding="utf-8-sig")
    pairs.to_csv(OUTPUT_DIR / "factor_corr_pairs_13_try1.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame({"selected_factor": subset}).to_csv(
        OUTPUT_DIR / "factor_low_corr_subset_try1.csv", index=False, encoding="utf-8-sig"
    )

    print("Correlation table:")
    print(corr.round(3).to_string())
    print()
    print(f"Largest subset with all abs(corr)<0.3: {len(subset)} factors, max_abs_corr={max_abs_corr:.3f}")
    print("\n".join(subset))
    print()
    print("Top high-correlation pairs:")
    print(pairs.head(15).to_string(index=False))


if __name__ == "__main__":
    main()
