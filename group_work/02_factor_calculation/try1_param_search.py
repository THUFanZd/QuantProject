"""Fast parameter search for selected near-threshold factors."""

from __future__ import annotations

import inspect
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
from group_work.factor_lib import factors as factor_module  # noqa: E402
from group_work.factor_lib.factors import FACTOR_REGISTRY  # noqa: E402
from group_work.factor_lib.data_loader import (  # noqa: E402
    load_dt,
    load_universe_mask,
    make_listed_mask,
    resolve_data_root as original_resolve_data_root,
)


OUTPUT_DIR = PROJECT_ROOT / "group_work" / "02_factor_calculation" / "outputs_try1"


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


def _ann_return(ret: pd.Series, periods: int = 252) -> float:
    return float(ret.mean() * periods)


def _ann_sharpe(ret: pd.Series, periods: int = 252) -> float:
    std = ret.std()
    if pd.isna(std) or std == 0:
        return np.nan
    return float(ret.mean() / std * np.sqrt(periods))


def evaluate_factor_fast(
    factor_name: str,
    params: dict,
    dt: dict[str, pd.DataFrame],
    data_root: Path,
    start_date: str = "2017-01-01",
    delay: int = 2,
    listed_days: int = 20,
) -> dict:
    fn = FACTOR_REGISTRY[factor_name]
    factor = fn(dt, **params).replace([np.inf, -np.inf], np.nan)
    listed = make_listed_mask(dt["vol"], listed_days=listed_days)
    universe_mask = load_universe_mask(factor, data_root=data_root)
    factor = factor.mask(universe_mask).mask(~listed)

    factor_stand = pn_TransNorm(factor).replace([np.inf, -np.inf], np.nan)
    long_w, short_w = get_ls_post(factor_stand)
    factor_port = long_w + short_w
    total_ret = dt["totalRet"]
    ls_ret = (factor_port.shift(delay) * total_ret).sum(axis=1)
    ic = factor_stand.corrwith(total_ret.shift(-delay), axis=1)
    start = pd.Timestamp(start_date)
    ls_ret = ls_ret.loc[ls_ret.index >= start]
    ic = ic.loc[ic.index >= start]

    ls_ar = _ann_return(ls_ret)
    ls_sr = _ann_sharpe(ls_ret)
    direction = -1 if pd.notna(ls_sr) and ls_sr < 0 else 1
    return {
        "factor": factor_name,
        "params": repr(params),
        "direction": direction,
        "ls_ar": ls_ar,
        "ls_sr": ls_sr,
        "selected_ar": direction * ls_ar,
        "selected_sr": direction * ls_sr,
        "ic_mean": float(ic.mean()),
        "ic_ir": _ann_sharpe(ic),
        "selected_ic_mean": float(direction * ic.mean()),
        "selected_ic_ir": direction * _ann_sharpe(ic),
        "latest_coverage": float(factor.iloc[-1].notna().mean()),
        "n_days": int(ls_ret.notna().sum()),
    }


def build_param_grid() -> dict[str, list[dict]]:
    return {
        "factor_47_nonlinear_volume_price_extreme_reversal": [
            {},
            {"poly_window": 20, "kurt_window": 15, "kurt_top_window": 3},
            {"poly_window": 30, "kurt_window": 15, "kurt_top_window": 3},
            {"poly_window": 40, "kurt_window": 20, "kurt_top_window": 3},
            {"poly_window": 30, "kurt_window": 30, "kurt_top_window": 5},
        ],
        "factor_13_main_fund_stability": [
            {},
            {"window": 5},
            {"window": 15},
            {"window": 20},
            {"window": 30},
        ],
        "factor_05_volume_price_divergence_cov": [
            {},
            {"delta_window": 1, "cov_window": 20},
            {"delta_window": 1, "cov_window": 40},
            {"delta_window": 2, "cov_window": 30},
            {"delta_window": 5, "cov_window": 30},
        ],
        "factor_43_turnover_relative_strength_reversal": [
            {},
            {"short_window": 5, "long_window": 120},
            {"short_window": 5, "long_window": 180},
            {"short_window": 10, "long_window": 180},
            {"short_window": 20, "long_window": 240},
        ],
        "factor_19_price_momentum_fund_volatility_reverse": [
            {},
            {"window": 5},
            {"window": 10},
            {"window": 20},
            {"window": 30},
        ],
        "factor_34_reverse_vroc_rank_vol_cov": [
            {},
            {"rank_vol_window": 5, "cov_window": 20},
            {"rank_vol_window": 10, "cov_window": 20},
            {"rank_vol_window": 15, "cov_window": 30},
            {"rank_vol_window": 20, "cov_window": 30},
        ],
        "factor_15_multi_dimensional_reversal": [
            {},
            {"window": 5},
            {"window": 10},
            {"window": 15},
            {"window": 30},
        ],
        "factor_52_large_outflow_momentum_reversal": [
            {},
            {},
            {},
            {},
            {},
        ],
    }


def validate_params(grid: dict[str, list[dict]]) -> None:
    for factor_name, variants in grid.items():
        sig = inspect.signature(FACTOR_REGISTRY[factor_name])
        allowed = set(sig.parameters) - {"dt"}
        for params in variants:
            unknown = set(params) - allowed
            if unknown:
                raise TypeError(f"{factor_name} does not accept {unknown}; allowed={allowed}")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    data_root = resolve_data_root()
    patch_factor_data_root(data_root)
    dt = load_dt(["adj_close", "open", "high", "close", "amount", "vol", "totalRet"], data_root=data_root)
    dt["totalRet"] = dt["totalRet"].mask(dt["totalRet"].abs() > 0.2)

    grid = build_param_grid()
    validate_params(grid)
    rows = []
    failures = []
    for factor_name, variants in grid.items():
        for i, params in enumerate(variants, start=1):
            label = f"{factor_name}#{i}"
            print(f"Evaluating {label}: {params}", flush=True)
            try:
                row = evaluate_factor_fast(factor_name, params, dt, data_root)
                row["variant"] = i
                rows.append(row)
            except Exception as exc:
                failures.append({"factor": factor_name, "variant": i, "params": repr(params), "error": repr(exc)})
                print(f"  failed: {exc!r}", flush=True)

    result = pd.DataFrame(rows).sort_values(["selected_sr", "selected_ar"], ascending=False)
    result.to_csv(OUTPUT_DIR / "factor_metrics_all_try1.csv", index=False, encoding="utf-8-sig")
    if failures:
        pd.DataFrame(failures).to_csv(OUTPUT_DIR / "factor_failures_try1.csv", index=False, encoding="utf-8-sig")
    print(result[["factor", "variant", "params", "direction", "selected_ar", "selected_sr", "latest_coverage"]].head(20).to_string(index=False))
    print(f"Saved: {OUTPUT_DIR / 'factor_metrics_all_try1.csv'}")


if __name__ == "__main__":
    main()
