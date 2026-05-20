# Stage 2 Factor Screening Results

- Data root: `C:\Users\CXY\Desktop\研一下\量化\课程资料（中证1000）\stock1000\data`
- Backtest start date: `2017-01-01`
- Holding delay: `2`
- Candidate factors evaluated: 36
- Selected factors: 10
- Strict `AR >= 10%` and `SR >= 2` candidates: 8
- Selection rule used here: `AR >= 10%`, sufficient latest coverage, then greedy screening with average cross-sectional `|corr| <= 0.40`.

## Selected 10 Factors

| Rank | Factor | Status | Direction | AR | SR | IC Mean | ICIR | Max Abs Corr In Selection |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 1 | `factor_04_reversal_turnover_enhanced` | proxy | +1 | 63.64% | 2.91 | 0.0257 | 2.66 | 0.40 |
| 2 | `factor_01_residual_volatility` | ready | +1 | 34.66% | 2.17 | 0.0152 | 2.12 | 0.40 |
| 3 | `factor_05_volume_price_divergence_cov` | local_ready | +1 | 36.89% | 2.08 | 0.0153 | 2.07 | 0.37 |
| 4 | `factor_52_large_outflow_momentum_reversal` | proxy | +1 | 21.98% | 1.69 | 0.0092 | 1.81 | 0.20 |
| 5 | `factor_10_deviation_volume_weighted` | ready | +1 | 37.45% | 1.64 | 0.0137 | 1.78 | 0.37 |
| 6 | `factor_31_main_elg_flow_rank_diff_decay` | proxy | +1 | 14.67% | 1.63 | 0.0089 | 1.51 | 0.16 |
| 7 | `factor_36_short_vol_adjusted_return` | ready | +1 | 20.56% | 1.49 | 0.0114 | 1.35 | 0.39 |
| 8 | `factor_14_main_fund_peak_reverse_rank` | proxy | +1 | 17.60% | 1.44 | 0.0115 | 1.44 | 0.39 |
| 9 | `factor_22_rank_momentum_reversal` | ready | +1 | 23.30% | 1.34 | 0.0128 | 1.45 | 0.38 |
| 10 | `factor_56_cashflow_price_trend` | local_proxy | +1 | 13.06% | 0.96 | 0.0069 | 0.80 | 0.32 |

## Notes

- `direction = -1` means the factor is used after sign reversal.
- Correlation is the average daily cross-sectional correlation between standardized factor values.
- `selected_ar`, `selected_sr`, `selected_ic_mean`, and `selected_ic_ir` are reported after direction adjustment.

## Top Candidate Metrics

| Factor | Status | Direction | AR | SR | IC Mean | ICIR | Coverage |
|---|---|---:|---:|---:|---:|---:|---:|
| `factor_04_reversal_turnover_enhanced` | proxy | +1 | 63.64% | 2.91 | 0.0257 | 2.66 | 94.9% |
| `factor_07_price_volume_deviation_vol` | ready | +1 | 47.66% | 2.44 | 0.0205 | 2.33 | 94.6% |
| `factor_12_turnover_volatility` | proxy | +1 | 41.86% | 2.26 | 0.0180 | 1.97 | 94.6% |
| `factor_13_main_fund_stability` | local_proxy | +1 | 42.08% | 2.25 | 0.0185 | 2.15 | 94.6% |
| `factor_01_residual_volatility` | ready | +1 | 34.66% | 2.17 | 0.0152 | 2.12 | 100.0% |
| `factor_03_turnover_volatility_momentum` | proxy | +1 | 33.19% | 2.10 | 0.0182 | 1.95 | 94.6% |
| `factor_05_volume_price_divergence_cov` | local_ready | +1 | 36.89% | 2.08 | 0.0153 | 2.07 | 100.0% |
| `factor_44_volume_divergence_composite_momentum` | proxy | +1 | 32.87% | 2.05 | 0.0167 | 1.95 | 94.0% |
| `factor_15_multi_dimensional_reversal` | proxy | +1 | 32.52% | 1.97 | 0.0177 | 1.86 | 94.4% |
| `factor_19_price_momentum_fund_volatility_reverse` | proxy | +1 | 29.10% | 1.93 | 0.0189 | 2.02 | 94.6% |
| `factor_43_turnover_relative_strength_reversal` | proxy | +1 | 25.89% | 1.90 | 0.0149 | 1.88 | 90.2% |
| `factor_16_price_volume_volatility_negative` | ready | +1 | 26.48% | 1.74 | 0.0149 | 1.55 | 100.0% |
| `factor_52_large_outflow_momentum_reversal` | proxy | +1 | 21.98% | 1.69 | 0.0092 | 1.81 | 94.3% |
| `factor_09_vol_adjusted_reversal` | ready | +1 | 28.67% | 1.68 | 0.0153 | 1.78 | 99.3% |
| `factor_10_deviation_volume_weighted` | ready | +1 | 37.45% | 1.64 | 0.0137 | 1.78 | 100.0% |
| `factor_31_main_elg_flow_rank_diff_decay` | proxy | +1 | 14.67% | 1.63 | 0.0089 | 1.51 | 93.8% |
| `factor_39_reverse_price_volume_rank` | ready | +1 | 24.75% | 1.55 | 0.0139 | 1.41 | 100.0% |
| `factor_17_price_fund_volatility_negative` | proxy | +1 | 24.15% | 1.52 | 0.0145 | 1.41 | 94.6% |
| `factor_50_reverse_standardized_decay_volume_price` | proxy | +1 | 27.65% | 1.52 | 0.0153 | 1.59 | 99.4% |
| `factor_36_short_vol_adjusted_return` | ready | +1 | 20.56% | 1.49 | 0.0114 | 1.35 | 100.0% |
