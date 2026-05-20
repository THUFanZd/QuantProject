            b = 255
        return r, g, b

    for i, row in enumerate(labels):
        draw.text((5, top + i * cell + 3), row[:36], fill="black")
        draw.text((left + i * cell + 3, 5), str(i + 1), fill="black")
        draw.text((left - 24, top + i * cell + 3), str(i + 1), fill="black")
        for j, col in enumerate(labels):
            x0 = left + j * cell
            y0 = top + i * cell
            draw.rectangle([x0, y0, x0 + cell - 1, y0 + cell - 1], fill=color(corr.loc[row, col]))
    draw.text((5, 5), "Selected factor correlation heatmap", fill="black")
    draw.text((5, 25), "Blue = negative, red = positive, diagonal = 1", fill="black")
    image.save(path)


def write_report(
    path: Path,
    metrics: pd.DataFrame,
    selected: pd.DataFrame,
    selected_corr: pd.DataFrame,
    data_root: Path,
    start_date: str,
    delay: int,
) -> None:
    lines = [
        "# Stage 2 Factor Screening Results",
        "",
        f"- Data root: `{data_root}`",
        f"- Backtest start date: `{start_date}`",
        f"- Holding delay: `{delay}`",
        f"- Candidate factors evaluated: {len(metrics)}",
        f"- Selected factors: {len(selected)}",
        f"- Strict `AR >= 10%` and `SR >= 2` candidates: {int(((metrics['selected_ar'] >= 0.10) & (metrics['selected_sr'] >= 2)).sum())}",
        "- Selection rule used here: `AR >= 10%`, sufficient latest coverage, then greedy screening with average cross-sectional `|corr| <= 0.40`.",
        "",
        "## Selected 10 Factors",
        "",
        "| Rank | Factor | Status | Direction | AR | SR | IC Mean | ICIR | Max Abs Corr In Selection |",
        "|---:|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in selected.iterrows():
        name = row["factor"]
        others = [c for c in selected_corr.columns if c != name]
        max_corr = selected_corr.loc[name, others].abs().max() if others else 0
        lines.append(
            "| {rank} | `{factor}` | {status} | {direction:+.0f} | {ar:.2%} | {sr:.2f} | {ic:.4f} | {icir:.2f} | {corr:.2f} |".format(
                rank=row["rank"],
                factor=name,
                status=row["status"],
                direction=row["direction"],
                ar=row["selected_ar"],
                sr=row["selected_sr"],
                ic=row["selected_ic_mean"],
                icir=row["selected_ic_ir"],
                corr=max_corr,
            )
        )

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- `direction = -1` means the factor is used after sign reversal.",
            "- Correlation is the average daily cross-sectional correlation between standardized factor values.",
            "- `selected_ar`, `selected_sr`, `selected_ic_mean`, and `selected_ic_ir` are reported after direction adjustment.",
            "",
            "## Top Candidate Metrics",
            "",
            "| Factor | Status | Direction | AR | SR | IC Mean | ICIR | Coverage |",
            "|---|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    top = metrics.sort_values("selected_sr", ascending=False).head(20)
    for _, row in top.iterrows():
        lines.append(
            "| `{factor}` | {status} | {direction:+.0f} | {ar:.2%} | {sr:.2f} | {ic:.4f} | {icir:.2f} | {cov:.1%} |".format(
                factor=row["factor"],
                status=row["status"],
                direction=row["direction"],
                ar=row["selected_ar"],
                sr=row["selected_sr"],
                ic=row["selected_ic_mean"],
                icir=row["selected_ic_ir"],
                cov=row["latest_coverage"],
            )
        )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-date", default="2017-01-01")
    parser.add_argument("--delay", type=int, default=2)
    parser.add_argument("--listed-days", type=int, default=20)
    parser.add_argument("--target", type=int, default=10)
    parser.add_argument("--max-abs-corr", type=float, default=0.40)
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    specs = build_specs()
    data_root = resolve_data_root()
    data = load_data(data_root, specs)

    metrics_rows: list[dict] = []
    returns: list[pd.Series] = []
    standardized_factors: dict[str, pd.DataFrame] = {}
    failures: list[dict] = []

    for spec in specs:
        print(f"Evaluating {spec.key} ...", flush=True)
        try:
            row, oriented_return, oriented_factor = evaluate_one(
                spec,
                data,
                start_date=args.start_date,
                delay=args.delay,
                listed_days=args.listed_days,
            )
        except Exception as exc:
            failures.append({"factor": spec.key, "error": repr(exc)})
            print(f"  failed: {exc!r}", flush=True)
            continue
        metrics_rows.append(row)
        returns.append(oriented_return)
        standardized_factors[spec.key] = oriented_factor

    metrics = pd.DataFrame(metrics_rows)
    metrics = metrics.sort_values("selected_sr", ascending=False)
    all_corr = build_corr_matrix(standardized_factors)
    selected = select_factors(metrics, all_corr, args.target, args.max_abs_corr)
    selected_corr = all_corr.loc[selected["factor"], selected["factor"]]

    returns_df = pd.concat(returns, axis=1)
    selected_returns = returns_df[selected["factor"].tolist()]

    metrics.to_csv(OUTPUT_DIR / "factor_metrics_all.csv", index=False, encoding="utf-8-sig")
    returns_df.to_csv(OUTPUT_DIR / "factor_returns_all.csv", encoding="utf-8-sig")
    all_corr.to_csv(OUTPUT_DIR / "factor_corr_all.csv", encoding="utf-8-sig")
    selected.to_csv(OUTPUT_DIR / "selected_10_factors.csv", index=False, encoding="utf-8-sig")
    selected_returns.to_csv(OUTPUT_DIR / "selected_10_returns.csv", encoding="utf-8-sig")
    selected_corr.to_csv(OUTPUT_DIR / "selected_10_corr.csv", encoding="utf-8-sig")
    save_heatmap(selected_corr, OUTPUT_DIR / "selected_10_corr.png")
    write_report(
        OUTPUT_DIR / "factor_results.md",
        metrics=metrics,
        selected=selected,
        selected_corr=selected_corr,
        data_root=data_root,
        start_date=args.start_date,
        delay=args.delay,
    )

    if failures:
        (OUTPUT_DIR / "factor_failures.json").write_text(
            json.dumps(failures, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    print(
        json.dumps(
            {
                "output_dir": str(OUTPUT_DIR),
                "evaluated": int(len(metrics)),
                "failures": failures,
                "selected": selected["factor"].tolist(),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    sys.exit(main())
