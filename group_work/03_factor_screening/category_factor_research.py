"""Experimental category factors for valuation, growth, quality, and flow structure."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Callable

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = PROJECT_ROOT / "group_work" / "02_factor_calculation"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import stage2_screen_factors as s  # noqa: E402


OUTPUT_DIR = SCRIPT_DIR / "category_factor_research_outputs"


@dataclass(frozen=True)
class Candidate:
    category: str
    name: str
    formula: str
    fn: Callable[[dict[str, pd.DataFrame]], pd.DataFrame]


def load_research_data(fields: set[str]) -> dict[str, pd.DataFrame]:
    data_root = s.resolve_data_root()
    idxwgt = pd.read_csv(data_root / "idxWgt.csv", index_col=0)
    idxwgt.index = s._date_index(idxwgt.index)
    stock_codes = idxwgt.columns.tolist()

    matrix_available = {p.stem for p in (data_root / "matrix").glob("*.pkl")}
    fin_available = {p.stem for p in (data_root / "finMatrix").glob("*.pkl")}
    data: dict[str, pd.DataFrame] = {}

    required = set(fields) | {"close", "vol", "totalRet"}
    for field in sorted(required):
        if field == "turnover":
            continue
        if field in matrix_available:
            frame = s.align_columns(s.load_frame(data_root, field, "matrix"), stock_codes)
        elif field in fin_available:
            frame = s.align_columns(s.load_frame(data_root, field, "finMatrix"), stock_codes)
        else:
            raise FileNotFoundError(f"Cannot find field: {field}")
        data[field] = frame.reindex(columns=stock_codes)

    base = data["close"]
    for key, frame in list(data.items()):
        data[key] = frame.reindex(index=base.index, columns=base.columns)

    if "turnover" in fields:
        if "turnover_rate_f" in data:
            data["turnover"] = data["turnover_rate_f"]
        else:
            data["turnover"] = s.safe_div(data["vol"] * 100, data["float_share"])

    data["idxwgt"] = idxwgt.reindex(index=base.index, columns=base.columns)
    data["totalRet"] = data["totalRet"].mask(data["totalRet"].abs() > 0.2)
    return data


def evaluate_candidate(candidate: Candidate, data: dict[str, pd.DataFrame]) -> dict:
    spec = s.FactorSpec("cat", candidate.name, candidate.category, tuple(), candidate.fn)
    row, _, _ = s.evaluate_one(spec, data, "2017-01-01", 2, 20)
    row["category"] = candidate.category
    row["name"] = candidate.name
    row["formula"] = candidate.formula
    return row


def build_candidates() -> list[Candidate]:
    c: list[Candidate] = []

    for window in [1, 5, 20, 60]:
        smooth = (lambda x, w=window: x if w == 1 else s.ts_mean(x, w))
        suffix = f"w{window}"
        c.extend(
            [
                Candidate(
                    "valuation",
                    f"value_pb_pe_ps_div_{suffix}",
                    f"mean(-rank(pb), -rank(pe_ttm>0), -rank(ps_ttm), rank(dv_ttm)); smoothed {window}",
                    lambda d, smooth=smooth: smooth(
                        -s.pn_rank(d["pb"])
                        - s.pn_rank(d["pe_ttm"].where(d["pe_ttm"] > 0))
                        - s.pn_rank(d["ps_ttm"])
                        + s.pn_rank(d["dv_ttm"])
                    ),
                ),
                Candidate(
                    "valuation",
                    f"value_pb_div_{suffix}",
                    f"-rank(pb) + rank(dv_ttm); smoothed {window}",
                    lambda d, smooth=smooth: smooth(-s.pn_rank(d["pb"]) + s.pn_rank(d["dv_ttm"])),
                ),
                Candidate(
                    "valuation",
                    f"value_ps_div_{suffix}",
                    f"-rank(ps_ttm) + rank(dv_ttm); smoothed {window}",
                    lambda d, smooth=smooth: smooth(-s.pn_rank(d["ps_ttm"]) + s.pn_rank(d["dv_ttm"])),
                ),
            ]
        )

    for window in [1, 5, 20, 60]:
        smooth = (lambda x, w=window: x if w == 1 else s.ts_mean(x, w))
        suffix = f"w{window}"
        c.extend(
            [
                Candidate(
                    "growth",
                    f"growth_yoy_composite_{suffix}",
                    f"rank(RevenueIncYoY)+rank(NetProfitIncYoY)+rank(EBITDAIncYoY); smoothed {window}",
                    lambda d, smooth=smooth: smooth(
                        s.pn_rank(d["RevenueIncYoY"])
                        + s.pn_rank(d["NetProfitIncYoY"])
                        + s.pn_rank(d["EBITDAIncYoY"])
                    ),
                ),
                Candidate(
                    "growth",
                    f"growth_qoq_composite_{suffix}",
                    f"rank(RevenueIncQoQ)+rank(NetProfitIncQoQ)+rank(EBITDAIncQoQ); smoothed {window}",
                    lambda d, smooth=smooth: smooth(
                        s.pn_rank(d["RevenueIncQoQ"])
                        + s.pn_rank(d["NetProfitIncQoQ"])
                        + s.pn_rank(d["EBITDAIncQoQ"])
                    ),
                ),
                Candidate(
                    "growth",
                    f"growth_profit_revenue_spread_{suffix}",
                    f"rank(NetProfitIncYoY)-rank(RevenueIncYoY)+rank(EBITDAIncYoY); smoothed {window}",
                    lambda d, smooth=smooth: smooth(
                        s.pn_rank(d["NetProfitIncYoY"])
                        - s.pn_rank(d["RevenueIncYoY"])
                        + s.pn_rank(d["EBITDAIncYoY"])
                    ),
                ),
            ]
        )

    for window in [1, 5, 20, 60]:
        smooth = (lambda x, w=window: x if w == 1 else s.ts_mean(x, w))
        suffix = f"w{window}"
        c.extend(
            [
                Candidate(
                    "quality",
                    f"quality_profit_cash_lowlev_{suffix}",
                    f"rank(ebit/total_assets)+rank(n_cashflow_act/total_assets)-rank(total_liab/total_assets); smoothed {window}",
                    lambda d, smooth=smooth: smooth(
                        s.pn_rank(s.safe_div(d["ebit"], d["total_assets"]))
                        + s.pn_rank(s.safe_div(d["n_cashflow_act"], d["total_assets"]))
                        - s.pn_rank(s.safe_div(d["total_liab"], d["total_assets"]))
                    ),
                ),
                Candidate(
                    "quality",
                    f"quality_cash_sales_lowlev_{suffix}",
                    f"rank(c_fr_sale_sg/total_mv)+rank(n_cashflow_act/total_assets)-rank(total_liab/total_assets); smoothed {window}",
                    lambda d, smooth=smooth: smooth(
                        s.pn_rank(s.safe_div(d["c_fr_sale_sg"], d["total_mv"]))
                        + s.pn_rank(s.safe_div(d["n_cashflow_act"], d["total_assets"]))
                        - s.pn_rank(s.safe_div(d["total_liab"], d["total_assets"]))
                    ),
                ),
                Candidate(
                    "quality",
                    f"quality_asset_turnover_cash_{suffix}",
                    f"rank(revenue/total_assets)+rank(n_cashflow_act/total_assets)-rank(fin_exp/total_assets); smoothed {window}",
                    lambda d, smooth=smooth: smooth(
                        s.pn_rank(s.safe_div(d["revenue"], d["total_assets"]))
                        + s.pn_rank(s.safe_div(d["n_cashflow_act"], d["total_assets"]))
                        - s.pn_rank(s.safe_div(d["fin_exp"], d["total_assets"]))
                    ),
                ),
            ]
        )

    for window in [3, 5, 10, 20, 60]:
        c.extend(
            [
                Candidate(
                    "flow_structure",
                    f"flow_elg_lg_imbalance_w{window}",
                    f"ts_mean((buy_elg_vol-sell_elg_vol + buy_lg_vol-sell_lg_vol) / vol, {window})",
                    lambda d, window=window: s.ts_mean(
                        s.safe_div(
                            (d["buy_elg_vol"] - d["sell_elg_vol"])
                            + (d["buy_lg_vol"] - d["sell_lg_vol"]),
                            d["vol"],
                        ),
                        window,
                    ),
                ),
                Candidate(
                    "flow_structure",
                    f"flow_big_vs_small_imbalance_w{window}",
                    f"ts_mean(((big net)-(small net)) / vol, {window})",
                    lambda d, window=window: s.ts_mean(
                        s.safe_div(
                            (d["buy_elg_vol"] + d["buy_lg_vol"] - d["sell_elg_vol"] - d["sell_lg_vol"])
                            - (d["buy_sm_vol"] - d["sell_sm_vol"]),
                            d["vol"],
                        ),
                        window,
                    ),
                ),
                Candidate(
                    "flow_structure",
                    f"flow_structure_stability_w{window}",
                    f"-ts_stdev((buy_elg_vol-sell_elg_vol + buy_lg_vol-sell_lg_vol) / vol, {window})",
                    lambda d, window=window: -s.ts_stdev(
                        s.safe_div(
                            (d["buy_elg_vol"] - d["sell_elg_vol"])
                            + (d["buy_lg_vol"] - d["sell_lg_vol"]),
                            d["vol"],
                        ),
                        window,
                    ),
                ),
            ]
        )

    return c


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    candidates = build_candidates()
    fields = {
        "pb",
        "pe_ttm",
        "ps_ttm",
        "dv_ttm",
        "total_mv",
        "RevenueIncYoY",
        "NetProfitIncYoY",
        "EBITDAIncYoY",
        "RevenueIncQoQ",
        "NetProfitIncQoQ",
        "EBITDAIncQoQ",
        "ebit",
        "total_assets",
        "n_cashflow_act",
        "total_liab",
        "c_fr_sale_sg",
        "revenue",
        "fin_exp",
        "buy_elg_vol",
        "sell_elg_vol",
        "buy_lg_vol",
        "sell_lg_vol",
        "buy_sm_vol",
        "sell_sm_vol",
    }
    data = load_research_data(fields)

    rows: list[dict] = []
    for candidate in candidates:
        print(f"Evaluating {candidate.category}: {candidate.name}", flush=True)
        try:
            rows.append(evaluate_candidate(candidate, data))
        except Exception as exc:
            rows.append(
                {
                    "category": candidate.category,
                    "name": candidate.name,
                    "factor": candidate.name,
                    "formula": candidate.formula,
                    "error": repr(exc),
                }
            )

    results = pd.DataFrame(rows)
    results.to_csv(OUTPUT_DIR / "category_factor_candidates.csv", index=False, encoding="utf-8-sig")

    scored = results.dropna(subset=["selected_sr"]).copy()
    top_each = (
        scored.sort_values(["category", "selected_sr"], ascending=[True, False])
        .groupby("category", as_index=False)
        .head(5)
    )
    top_each.to_csv(OUTPUT_DIR / "category_factor_top5_each.csv", index=False, encoding="utf-8-sig")
    best = (
        scored.sort_values(["category", "selected_sr"], ascending=[True, False])
        .groupby("category", as_index=False)
        .head(1)
    )
    best.to_csv(OUTPUT_DIR / "category_factor_best_each.csv", index=False, encoding="utf-8-sig")

    print(best[["category", "name", "selected_ar", "selected_sr", "selected_ic_ir", "latest_coverage", "formula"]].to_string(index=False))


if __name__ == "__main__":
    main()
