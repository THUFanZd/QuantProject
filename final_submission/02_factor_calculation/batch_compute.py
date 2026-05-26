"""Batch-compute factor metrics and render the selected-factor correlation heatmap."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
STAGE_DIR = Path(__file__).resolve().parent
SELECTED_PATH = STAGE_DIR / "support" / "selected_factors.csv"
CORR_SOURCE_PATH = STAGE_DIR / "support" / "corr_20_passed_factors.csv"
for path in (PROJECT_ROOT, STAGE_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from evaluate_factor import LS_METHODS, evaluate_factor, save_outputs  # noqa: E402
from group_work.factor_lib import FACTOR_REGISTRY  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Batch compute Stage-2 factor evaluation results.")
    parser.add_argument("--start-date", default="2017-01-01")
    parser.add_argument("--delay", type=int, default=2)
    parser.add_argument("--listed-days", type=int, default=20)
    parser.add_argument("--ls-method", choices=LS_METHODS, default="sign_weight")
    parser.add_argument("--quantile", type=float, default=0.3)
    parser.add_argument(
        "--factor",
        action="append",
        choices=sorted(FACTOR_REGISTRY),
        help="Factor key to calculate; may be passed repeatedly. Default calculates every registered factor.",
    )
    parser.add_argument(
        "--selected-only",
        action="store_true",
        help="Calculate the final ten selected factors instead of all registered factors.",
    )
    parser.add_argument(
        "--plot-only",
        action="store_true",
        help="Only render corr_matrix.png from existing selected-factor correlation results.",
    )
    parser.add_argument("--summary-output", type=Path, default=STAGE_DIR / "batch_metrics.csv")
    parser.add_argument("--corr-output", type=Path, default=STAGE_DIR / "corr_matrix.png")
    return parser.parse_args()


def selected_factor_keys() -> list[str]:
    return pd.read_csv(SELECTED_PATH)["factor_key"].tolist()


def resolve_factor_keys(args: argparse.Namespace) -> list[str]:
    if args.factor:
        return args.factor
    if args.selected_only:
        return selected_factor_keys()
    return sorted(FACTOR_REGISTRY)


def plot_selected_corr(output_path: Path) -> tuple[int, float]:
    keys = selected_factor_keys()
    corr = pd.read_csv(CORR_SOURCE_PATH, index_col=0).loc[keys, keys]
    off_diagonal = corr.where(np.triu(np.ones(corr.shape, dtype=bool), 1)).stack().abs()

    short_labels = [f"F{i + 1}" for i in range(len(keys))]
    fig, ax = plt.subplots(figsize=(9.5, 8))
    image = ax.imshow(corr.to_numpy(), cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(len(keys)), short_labels, rotation=45, ha="right")
    ax.set_yticks(range(len(keys)), short_labels)
    for i in range(len(keys)):
        for j in range(len(keys)):
            ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center", fontsize=7)
    ax.set_title("Selected 10 Factors: Mean Cross-sectional Correlation")
    legend = "\n".join(f"F{i + 1}: {key}" for i, key in enumerate(keys))
    ax.text(1.05, 1.0, legend, transform=ax.transAxes, va="top", fontsize=8)
    fig.colorbar(image, ax=ax, fraction=0.045, pad=0.24)
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return len(keys), float(off_diagonal.max())


def main() -> None:
    args = parse_args()
    selected_count, max_abs_corr = plot_selected_corr(args.corr_output)
    print(f"Saved selected-factor heatmap: {args.corr_output}")
    print(f"Selected factors: {selected_count}; max abs correlation: {max_abs_corr:.6f}")

    if args.plot_only:
        return

    metric_frames: list[pd.DataFrame] = []
    for factor_key in resolve_factor_keys(args):
        print(f"Evaluating factor: {factor_key}", flush=True)
        metrics, returns, _ = evaluate_factor(
            factor_name=factor_key,
            start_date=args.start_date,
            delay=args.delay,
            listed_days=args.listed_days,
            ls_method=args.ls_method,
            quantile=args.quantile,
        )
        save_outputs(factor_key, metrics, returns, args.ls_method)
        metric_frames.append(metrics)

    summary = pd.concat(metric_frames, ignore_index=True)
    args.summary_output.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(args.summary_output, index=False, encoding="utf-8-sig")
    print(f"Saved batch metrics for {len(summary)} factors: {args.summary_output}")


if __name__ == "__main__":
    main()
