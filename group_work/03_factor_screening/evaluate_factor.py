"""Evaluate one implemented factor with the course-style long-short protocol."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
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
    resolve_data_root,
)


def _ann_sharpe(ret: pd.Series, periods: int = 252) -> float:
    std = ret.std()
    if pd.isna(std) or std == 0:
        return np.nan
    return ret.mean() / std * np.sqrt(periods)


def _ann_return(ret: pd.Series, periods: int = 252) -> float:
    return ret.mean() * periods


def evaluate_factor(
    factor_name: str,
    start_date: str = "2017-01-01",
    delay: int = 2,
    listed_days: int = 20,
) -> tuple[pd.DataFrame, pd.DataFrame, Path]:
    if factor_name not in FACTOR_REGISTRY:
        available = ", ".join(sorted(FACTOR_REGISTRY))
        raise KeyError(f"Unknown factor {factor_name!r}. Available: {available}")

    data_root = resolve_data_root()
    dt = load_dt(["adj_close", "open", "high", "close", "amount", "vol", "totalRet"], data_root=data_root)
    dt["totalRet"] = dt["totalRet"].mask(dt["totalRet"].abs() > 0.2)

    factor = FACTOR_REGISTRY[factor_name](dt)
    listed = make_listed_mask(dt["vol"], listed_days=listed_days)
    universe_mask = load_universe_mask(factor, data_root=data_root)
    factor = factor.mask(universe_mask).mask(~listed)

    factor_stand = pn_TransNorm(factor)
    long_w, short_w = get_ls_post(factor_stand)
    factor_port = long_w + short_w

    total_ret = dt["totalRet"]
    average_ret = total_ret.mask(~listed).mean(axis=1)
    ls_ret = (factor_port.shift(delay) * total_ret).sum(axis=1)
    long_excess_ret = (long_w.shift(delay) * total_ret).sum(axis=1) - average_ret
    short_excess_ret = (short_w.shift(delay) * total_ret).sum(axis=1) + average_ret
    ic = factor_stand.corrwith(total_ret.shift(-delay), axis=1)

    start = pd.Timestamp(start_date)
    returns = pd.DataFrame(
        {
            "ls_ret": ls_ret,
            "long_excess_ret": long_excess_ret,
            "short_excess_ret": short_excess_ret,
            "ic": ic,
        }
    )
    returns = returns.loc[returns.index >= start]

    latest_coverage = factor.iloc[-1].notna().mean()
    metrics = pd.DataFrame(
        [
            {
                "factor": factor_name,
                "data_root": str(data_root),
                "start_date": start_date,
                "delay": delay,
                "listed_days": listed_days,
                "n_days": int(returns["ls_ret"].notna().sum()),
                "latest_coverage": float(latest_coverage),
                "ls_ar": _ann_return(returns["ls_ret"]),
                "ls_sr": _ann_sharpe(returns["ls_ret"]),
                "long_excess_ar": _ann_return(returns["long_excess_ret"]),
                "long_excess_sr": _ann_sharpe(returns["long_excess_ret"]),
                "short_excess_ar": _ann_return(returns["short_excess_ret"]),
                "short_excess_sr": _ann_sharpe(returns["short_excess_ret"]),
                "ic_mean": returns["ic"].mean(),
                "ic_ir": _ann_sharpe(returns["ic"]),
            }
        ]
    )

    return metrics, returns, data_root


def save_outputs(factor_name: str, metrics: pd.DataFrame, returns: pd.DataFrame) -> dict[str, Path]:
    output_dir = PROJECT_ROOT / "group_work" / "02_factor_calculation" / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    metrics_path = output_dir / f"{factor_name}_metrics.csv"
    returns_path = output_dir / f"{factor_name}_daily_returns.csv"
    plot_path = output_dir / f"{factor_name}_cumret.png"

    metrics.to_csv(metrics_path, index=False, encoding="utf-8-sig")
    returns.to_csv(returns_path, encoding="utf-8-sig")

    fig, ax = plt.subplots(figsize=(10, 5))
    returns[["ls_ret", "long_excess_ret", "short_excess_ret"]].fillna(0).cumsum().plot(ax=ax)
    ax.set_title(f"{factor_name} cumulative returns")
    ax.set_xlabel("date")
    ax.set_ylabel("cumulative return")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(plot_path, dpi=150)
    plt.close(fig)

    return {
        "metrics": metrics_path,
        "daily_returns": returns_path,
        "plot": plot_path,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--factor",
        default="factor_42_adjusted_price_reversal",
        choices=sorted(FACTOR_REGISTRY),
    )
    parser.add_argument("--start-date", default="2017-01-01")
    parser.add_argument("--delay", type=int, default=2)
    parser.add_argument("--listed-days", type=int, default=20)
    args = parser.parse_args()

    metrics, returns, _ = evaluate_factor(
        factor_name=args.factor,
        start_date=args.start_date,
        delay=args.delay,
        listed_days=args.listed_days,
    )
    output_paths = save_outputs(args.factor, metrics, returns)

    payload = {
        "metrics": metrics.iloc[0].to_dict(),
        "outputs": {key: str(value) for key, value in output_paths.items()},
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
