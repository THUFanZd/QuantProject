"""Evaluate the 15 factor_add factors with the existing course evaluator."""

from __future__ import annotations

import json
from pathlib import Path
import sys

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
WORKSPACE_ROOT = PROJECT_ROOT.parent
FEATURE_DIR = PROJECT_ROOT / "code" / "stock1800"
EVAL_DIR = PROJECT_ROOT / "group_work" / "02_factor_calculation"
CURRENT_DIR = Path(__file__).resolve().parent
for path in (PROJECT_ROOT, FEATURE_DIR, EVAL_DIR, CURRENT_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import evaluate_factor as evaluator  # noqa: E402
from factor_add import FACTOR_ADD_REGISTRY, set_data_root  # noqa: E402
from group_work.factor_lib.data_loader import load_dt as original_load_dt  # noqa: E402


OUTPUT_DIR = CURRENT_DIR / "outputs"
REQUIRED_FIELDS = [
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


def patched_load_dt(fields: list[str], data_root: Path | None = None) -> dict[str, pd.DataFrame]:
    merged_fields = list(dict.fromkeys([*fields, *REQUIRED_FIELDS]))
    return original_load_dt(merged_fields, data_root=data_root)


def save_outputs(factor_name: str, metrics: pd.DataFrame, returns: pd.DataFrame) -> dict[str, Path]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    metrics_path = OUTPUT_DIR / f"{factor_name}_metrics.csv"
    returns_path = OUTPUT_DIR / f"{factor_name}_daily_returns.csv"
    metrics.to_csv(metrics_path, index=False, encoding="utf-8-sig")
    returns.to_csv(returns_path, encoding="utf-8-sig")
    return {"metrics": metrics_path, "daily_returns": returns_path}


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    data_root = resolve_course_data_root()
    set_data_root(data_root)
    evaluator.resolve_data_root = lambda: data_root
    evaluator.load_dt = patched_load_dt
    evaluator.FACTOR_REGISTRY.update(FACTOR_ADD_REGISTRY)

    rows = []
    outputs = {}
    failures = []
    for factor_name in FACTOR_ADD_REGISTRY:
        try:
            metrics, returns, _ = evaluator.evaluate_factor(factor_name)
            metrics = metrics.copy()
            metrics["passes_abs_ar_gt_10pct_abs_sr_gt_2"] = (
                metrics["ls_ar"].abs().ge(0.10) & metrics["ls_sr"].abs().ge(2.0)
            )
            paths = save_outputs(factor_name, metrics, returns)
            rows.append(metrics.iloc[0])
            outputs[factor_name] = {key: str(value) for key, value in paths.items()}
        except Exception as exc:
            failures.append({"factor": factor_name, "error": repr(exc)})

    summary = pd.DataFrame(rows)
    summary_path = OUTPUT_DIR / "factor_add_summary.csv"
    summary.to_csv(summary_path, index=False, encoding="utf-8-sig")
    if failures:
        pd.DataFrame(failures).to_csv(OUTPUT_DIR / "factor_add_failures.csv", index=False, encoding="utf-8-sig")

    payload = {
        "data_root": str(data_root),
        "summary": str(summary_path),
        "outputs": outputs,
        "failures": failures,
        "metrics": summary[
            [
                "factor",
                "ls_ar",
                "ls_sr",
                "latest_coverage",
                "passes_abs_ar_gt_10pct_abs_sr_gt_2",
            ]
        ].to_dict(orient="records") if len(summary) else [],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
