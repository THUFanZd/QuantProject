# Factor Implementation Progress

This file is the handoff for the user and the existing factors' info for Codex.

## Status Legend

- `success`: implemented with available local data and registered.
- `proxy`: implemented with documented local substitute fields.
- `missing_easy`: missing data, but easy to resolve if a clear field/file is added.
- `missing_unsolved`: missing data and not credibly recoverable from current local data.
- `not_tested`: implementation exists, but evaluator has not passed yet.

## Test Command

```powershell
conda run -n bishe python group_work\02_factor_calculation\evaluate_factor.py --factor <factor_key>
```

Full-pass validation was also run in one `bishe` Python process via `evaluate_factor(...)` and `save_outputs(...)` for all registered keys to avoid repeated conda startup overhead.
You can change evaluate parameters via changing cli arguments.

## Summary

- Last updated: 2026-05-24 low-correlation target pass with 20 stage-2 deliverable factors
- Factors total: 75 registered keys (55 source keys + 10 screened add-ons + 10 optimized stage-2 variants)
- Implemented exact: 20
- Implemented proxy: 34
- Missing but easy: 0
- Missing and unsolved: 2 (`21`, `26`)
- Not started / not tested: 0
- Registered source factor keys: 55 (all except blocked source ID `21`)
- Registered screened add-on factor keys: 10 (`factor_add_06_quality_x_flow`, 3 `factor_add2_*`, 6 `factor_add3_*`)
- Registered optimized variant keys: 10 (`factor_opt_*`)
- Registered keys passing evaluator: 75 / 75 (prior source/add-on/optimized keys plus 6 new `factor_add3_*` keys validated on 2026-05-24)
- AR/SR-qualified deliverable keys: 20 / 20, using `sign_weight`, `delay=2`, `start_date=2017-01-01`
- Low-correlation target: pass; among the 20 AR/SR-qualified keys, the largest subset with pairwise `abs(corr) < 0.3` has 11 factors.

## Factor Table

| ID | Source file pattern | Function / registry key | Status | Test result | Notes |
|---:|---|---|---|---|---|
| 01 | `*01*.md` | `factor_01_residual_volatility` | success | pass; SR 2.377, ICIR 2.277, coverage 1.000; metrics: `group_work/02_factor_calculation/outputs/factor_01_residual_volatility_metrics.csv` |  |
| 02 | `*02*.md` | `factor_02_volume_amount_efficiency` | success | pass; SR 0.529, ICIR 0.519, coverage 1.000; metrics: `group_work/02_factor_calculation/outputs/factor_02_volume_amount_efficiency_metrics.csv` |  |
| 03 | `*03*.md` | `factor_03_turnover_volatility_momentum` | proxy | pass; SR 1.528, ICIR 1.351, coverage 0.946; metrics: `group_work/02_factor_calculation/outputs/factor_03_turnover_volatility_momentum_metrics.csv` |  |
| 04 | `*04*.md` | `factor_04_reversal_turnover_enhanced` | proxy | pass; SR 1.399, ICIR 1.106, coverage 0.949; metrics: `group_work/02_factor_calculation/outputs/factor_04_reversal_turnover_enhanced_metrics.csv` |  |
| 05 | `*05*.md` | `factor_05_volume_price_divergence_cov` | success | pass; SR 1.920, ICIR 1.821, coverage 1.000; metrics: `group_work/02_factor_calculation/outputs/factor_05_volume_price_divergence_cov_metrics.csv` |  |
| 06 | `*06*.md` | `factor_06_ma_filter_reversal` | success | pass; SR 1.449, ICIR 1.251, coverage 1.000; metrics: `group_work/02_factor_calculation/outputs/factor_06_ma_filter_reversal_metrics.csv` |  |
| 07 | `*07*.md` | `factor_07_price_volume_deviation_vol` | success | pass; SR 2.089, ICIR 2.031, coverage 0.946; metrics: `group_work/02_factor_calculation/outputs/factor_07_price_volume_deviation_vol_metrics.csv` |  |
| 08 | `*08*.md` | `factor_08_liquidity_stability` | success | pass; SR 1.245, ICIR 1.060, coverage 1.000; metrics: `group_work/02_factor_calculation/outputs/factor_08_liquidity_stability_metrics.csv` |  |
| 09 | `*09*.md` | `factor_09_vol_adjusted_reversal` | success | pass; SR 1.293, ICIR 1.365, coverage 0.993; metrics: `group_work/02_factor_calculation/outputs/factor_09_vol_adjusted_reversal_metrics.csv` |  |
| 10 | `*10*.md` | `factor_10_deviation_volume_weighted` | success | pass; SR 1.309, ICIR 1.440, coverage 1.000; metrics: `group_work/02_factor_calculation/outputs/factor_10_deviation_volume_weighted_metrics.csv` |  |
| 11 | `*11*.md` | `factor_11_volatility_turnover_coupling` | success | pass; SR 1.134, ICIR 0.962, coverage 0.949; metrics: `group_work/02_factor_calculation/outputs/factor_11_volatility_turnover_coupling_metrics.csv` |  |
| 12 | `*12*.md` | `factor_12_turnover_volatility` | proxy | pass; SR 1.587, ICIR 1.291, coverage 0.946; metrics: `group_work/02_factor_calculation/outputs/factor_12_turnover_volatility_metrics.csv` |  |
| 13 | `*13*.md` | `factor_13_main_fund_stability` | proxy | pass; SR 1.966, ICIR 1.921, coverage 0.946; metrics: `group_work/02_factor_calculation/outputs/factor_13_main_fund_stability_metrics.csv` |  |
| 14 | `*14*.md` | `factor_14_main_fund_peak_reverse_rank` | proxy | pass; SR 1.444, ICIR 1.430, coverage 0.946; metrics: `group_work/02_factor_calculation/outputs/factor_14_main_fund_peak_reverse_rank_metrics.csv` |  |
| 15 | `*15*.md` | `factor_15_multi_dimensional_reversal` | proxy | pass; SR 1.470, ICIR 1.333, coverage 0.944; metrics: `group_work/02_factor_calculation/outputs/factor_15_multi_dimensional_reversal_metrics.csv` |  |
| 16 | `*16*.md` | `factor_16_price_volume_volatility_negative` | success | pass; SR 1.490, ICIR 1.281, coverage 1.000; metrics: `group_work/02_factor_calculation/outputs/factor_16_price_volume_volatility_negative_metrics.csv` |  |
| 17 | `*17*.md` | `factor_17_price_fund_volatility_negative` | proxy | pass; SR 1.419, ICIR 1.306, coverage 0.946; metrics: `group_work/02_factor_calculation/outputs/factor_17_price_fund_volatility_negative_metrics.csv` |  |
| 18 | `*18*.md` | `factor_18_price_volume_decay_synergy` | success | pass; SR 1.546, ICIR 1.601, coverage 0.949; metrics: `group_work/02_factor_calculation/outputs/factor_18_price_volume_decay_synergy_metrics.csv` |  |
| 19 | `*19*.md` | `factor_19_price_momentum_fund_volatility_reverse` | proxy | pass; SR 1.753, ICIR 1.899, coverage 0.946; metrics: `group_work/02_factor_calculation/outputs/factor_19_price_momentum_fund_volatility_reverse_metrics.csv` |  |
| 20 | `*20*.md` | `factor_20_main_flow_decay` | proxy | pass; SR 1.725, ICIR 1.547, coverage 0.938; metrics: `group_work/02_factor_calculation/outputs/factor_20_main_flow_decay_metrics.csv` |  |
| 21 | `*21*.md` |  | missing_unsolved | not run | Blocked: source `REINSTATEMENT_CHG_60D` has no credible local equivalent. |
| 22 | `*22*.md` | `factor_22_rank_momentum_reversal` | success | pass; SR 1.110, ICIR 1.172, coverage 1.000; metrics: `group_work/02_factor_calculation/outputs/factor_22_rank_momentum_reversal_metrics.csv` |  |
| 23 | `*23*.md` | `factor_23_main_flow_decay_percentage` | proxy | pass; SR 0.990, ICIR 0.950, coverage 0.939; metrics: `group_work/02_factor_calculation/outputs/factor_23_main_flow_decay_percentage_metrics.csv` |  |
| 24 | `*24*.md` | `factor_24_main_elg_flow_diff_decay` | proxy | pass; SR 1.567, ICIR 1.385, coverage 0.938; metrics: `group_work/02_factor_calculation/outputs/factor_24_main_elg_flow_diff_decay_metrics.csv` |  |
| 25 | `*25*.md` | `factor_25_main_flow_volatility_momentum` | proxy | pass; SR 0.015, ICIR 0.322, coverage 0.914; metrics: `group_work/02_factor_calculation/outputs/factor_25_main_flow_volatility_momentum_metrics.csv` |  |
| 26 | `*26*.md` | `factor_26_dual_style_ir_spread` | missing_unsolved | pass; SR 0.043, ICIR -0.042, coverage 0.000; metrics: `group_work/02_factor_calculation/outputs/factor_26_dual_style_ir_spread_metrics.csv` | Registered diagnostic implementation exists, but latest coverage is 0.0 because local Barra dates do not align with the current stock matrix. |
| 27 | `*27*.md` | `factor_27_main_elg_flow_diff_decay` | proxy | pass; SR 1.778, ICIR 1.606, coverage 0.941; metrics: `group_work/02_factor_calculation/outputs/factor_27_main_elg_flow_diff_decay_metrics.csv` |  |
| 28 | `*28*.md` | `factor_28_main_elg_flow_synergy` | proxy | pass; SR 0.186, ICIR 0.006, coverage 0.934; metrics: `group_work/02_factor_calculation/outputs/factor_28_main_elg_flow_synergy_metrics.csv` |  |
| 29 | `*29*.md` | `factor_29_main_flow_volatility_decay` | proxy | pass; SR 1.610, ICIR 1.339, coverage 0.914; metrics: `group_work/02_factor_calculation/outputs/factor_29_main_flow_volatility_decay_metrics.csv` |  |
| 30 | `*30*.md` | `factor_30_volatility_main_flow_momentum` | proxy | pass; SR 0.116, ICIR 0.417, coverage 0.912; metrics: `group_work/02_factor_calculation/outputs/factor_30_volatility_main_flow_momentum_metrics.csv` |  |
| 31 | `*31*.md` | `factor_31_main_elg_flow_rank_diff_decay` | proxy | pass; SR 1.652, ICIR 1.527, coverage 0.938; metrics: `group_work/02_factor_calculation/outputs/factor_31_main_elg_flow_rank_diff_decay_metrics.csv` |  |
| 32 | `*32*.md` | `factor_32_momentum_flow_composite` | proxy | pass; SR 1.725, ICIR 1.547, coverage 0.938; metrics: `group_work/02_factor_calculation/outputs/factor_32_momentum_flow_composite_metrics.csv` |  |
| 33 | `*33*.md` | `factor_33_reinstatement_residual_vol_ratio` | proxy | pass; SR 2.402, ICIR 2.796, coverage 1.000; metrics: `group_work/02_factor_calculation/outputs/factor_33_reinstatement_residual_vol_ratio_metrics.csv` |  |
| 34 | `*34*.md` | `factor_34_reverse_vroc_rank_vol_cov` | success | pass; SR 1.802, ICIR 1.761, coverage 0.940; metrics: `group_work/02_factor_calculation/outputs/factor_34_reverse_vroc_rank_vol_cov_metrics.csv` |  |
| 35 | `*35*.md` | `factor_35_price_spread_momentum` | success | pass; SR 1.283, ICIR 1.305, coverage 1.000; metrics: `group_work/02_factor_calculation/outputs/factor_35_price_spread_momentum_metrics.csv` |  |
| 36 | `*36*.md` | `factor_36_short_vol_adjusted_return` | success | pass; SR 1.126, ICIR 0.950, coverage 1.000; metrics: `group_work/02_factor_calculation/outputs/factor_36_short_vol_adjusted_return_metrics.csv` |  |
| 37 | `*37*.md` | `factor_37_volume_stable_close` | success | pass; SR 0.141, ICIR 0.124, coverage 1.000; metrics: `group_work/02_factor_calculation/outputs/factor_37_volume_stable_close_metrics.csv` |  |
| 38 | `*38*.md` | `factor_38_volatility_difference_proxy` | proxy | pass; SR -0.289, ICIR -0.307, coverage 1.000; metrics: `group_work/02_factor_calculation/outputs/factor_38_volatility_difference_proxy_metrics.csv` | Proxy for unavailable `FACTOR_VOL60D` / `FACTOR_TVSD20D`. |
| 39 | `*39*.md` | `factor_39_reverse_price_volume_rank` | success | pass; SR 1.230, ICIR 1.081, coverage 1.000; metrics: `group_work/02_factor_calculation/outputs/factor_39_reverse_price_volume_rank_metrics.csv` |  |
| 40 | `*40*.md` | `factor_40_fund_flow_max_drawdown` | proxy | pass; SR 1.194, ICIR 1.137, coverage 0.946; metrics: `group_work/02_factor_calculation/outputs/factor_40_fund_flow_max_drawdown_metrics.csv` |  |
| 41 | `*41*.md` | `factor_41_high_open_momentum_decay` | success | pass; SR 0.759, ICIR 0.643, coverage 1.000; metrics: `group_work/02_factor_calculation/outputs/factor_41_high_open_momentum_decay_metrics.csv` |  |
| 42 | `*42*.md` | `factor_42_adjusted_price_reversal` | success | pass; SR 0.956, ICIR 1.011, coverage 1.000; metrics: `group_work/02_factor_calculation/outputs/factor_42_adjusted_price_reversal_metrics.csv` |  |
| 43 | `*43*.md` | `factor_43_turnover_relative_strength_reversal` | proxy | pass; SR 1.587, ICIR 1.583, coverage 0.902; metrics: `group_work/02_factor_calculation/outputs/factor_43_turnover_relative_strength_reversal_metrics.csv` |  |
| 44 | `*44*.md` | `factor_44_volume_divergence_composite_momentum` | proxy | pass; SR 1.471, ICIR 1.324, coverage 0.929; metrics: `group_work/02_factor_calculation/outputs/factor_44_volume_divergence_composite_momentum_metrics.csv` |  |
| 45 | `*45*.md` | `factor_45_log_momentum_reverse_rank` | proxy | pass; SR 0.713, ICIR 0.683, coverage 1.000; metrics: `group_work/02_factor_calculation/outputs/factor_45_log_momentum_reverse_rank_metrics.csv` |  |
| 46 | `*46*.md` | `factor_46_price_momentum_decay_reversal` | success | pass; SR 0.486, ICIR 0.524, coverage 1.000; metrics: `group_work/02_factor_calculation/outputs/factor_46_price_momentum_decay_reversal_metrics.csv` |  |
| 47 | `*47*.md` | `factor_47_nonlinear_volume_price_extreme_reversal` | proxy | pass; SR 1.993, ICIR 2.146, coverage 0.944; metrics: `group_work/02_factor_calculation/outputs/factor_47_nonlinear_volume_price_extreme_reversal_metrics.csv` | Proxy: `TS_POLY_REGRESSION` semantics are under-specified; uses nonlinear rolling close-volume relation. |
| 48 | `*48*.md` | `factor_48_turnover_adjusted_abnormal_price_momentum` | proxy | pass; SR -0.703, ICIR -0.691, coverage 0.949; metrics: `group_work/02_factor_calculation/outputs/factor_48_turnover_adjusted_abnormal_price_momentum_metrics.csv` |  |
| 49 | `*49*.md` | `factor_49_volatility_trend_composite` | proxy | pass; SR 0.519, ICIR 0.620, coverage 0.917; metrics: `group_work/02_factor_calculation/outputs/factor_49_volatility_trend_composite_metrics.csv` |  |
| 50 | `*50*.md` | `factor_50_reverse_standardized_decay_volume_price` | proxy | pass; SR 0.947, ICIR 1.021, coverage 0.994; metrics: `group_work/02_factor_calculation/outputs/factor_50_reverse_standardized_decay_volume_price_metrics.csv` |  |
| 51 | `*51*.md` | `factor_51_nonlinear_price_volume_flow` | proxy | pass; SR -1.346, ICIR -1.581, coverage 0.938; metrics: `group_work/02_factor_calculation/outputs/factor_51_nonlinear_price_volume_flow_metrics.csv` |  |
| 52 | `*52*.md` | `factor_52_large_outflow_momentum_reversal` | proxy | pass; SR 1.368, ICIR 1.503, coverage 0.943; metrics: `group_work/02_factor_calculation/outputs/factor_52_large_outflow_momentum_reversal_metrics.csv` |  |
| 53 | `*53*.md` | `factor_53_price_flow_cross_quantile` | proxy | pass; SR -0.181, ICIR -0.145, coverage 0.946; metrics: `group_work/02_factor_calculation/outputs/factor_53_price_flow_cross_quantile_metrics.csv` |  |
| 54 | `*54*.md` | `factor_54_industry_fund_quality_reverse` | proxy | pass; SR -2.017, ICIR -1.941, coverage 0.944; metrics: `group_work/02_factor_calculation/outputs/factor_54_industry_fund_quality_reverse_metrics.csv` | Proxy: 5Y ROE/ROA fields replaced by local TTM/Q1 profitability ratios. |
| 55 | `*55*.md` | `factor_55_industry_ma_value_proxy` | proxy | pass; SR 1.024, ICIR 1.038, coverage 0.901; metrics: `group_work/02_factor_calculation/outputs/factor_55_industry_ma_value_proxy_metrics.csv` |  |
| 56 | `*56*.md` | `factor_56_cashflow_price_trend` | proxy | pass; SR 0.712, ICIR 0.611, coverage 0.922; metrics: `group_work/02_factor_calculation/outputs/factor_56_cashflow_price_trend_metrics.csv` |  |

## Screened Add-on Factors

| Registry key | Function | Status | Test result | Notes |
|---|---|---|---|---|
| `factor_add_06_quality_x_flow` | `factor_add_06_quality_x_flow` | screened_addon | pass; AR 16.25%, SR 2.008, ICIR 1.797, coverage 0.917; metrics: `group_work/02_factor_calculation/outputs/sign_weight/factor_add_06_quality_x_flow_metrics.csv` | Migrated from the `main` branch `group_work/factor_add/` experiment into the formal `FACTOR_REGISTRY`. Formula: profitability quality rank (`NetProfitTTMQ1 / NetAssetQ1`) multiplied by 20-day main net fund-flow rank. |
| `factor_add2_adj_05_f34_15_25_industry` | `factor_add2_adj_05_f34_15_25_industry` | screened_addon | pass; AR 11.56%, SR 2.026, ICIR 1.939, coverage 0.940; metrics: `group_work/02_factor_calculation/outputs/sign_weight/factor_add2_adj_05_f34_15_25_industry_metrics.csv` | Migrated from the `main` branch `group_work/factor_add_new/` experiment into the formal `FACTOR_REGISTRY`. Formula: industry-ranked f34 variant with 15-day close-rank volatility and 25-day VROC covariance. |
| `factor_add2_adj_07_f18_decay30_industry` | `factor_add2_adj_07_f18_decay30_industry` | screened_addon | pass; AR 15.28%, SR 2.007, ICIR 2.173, coverage 0.949; metrics: `group_work/02_factor_calculation/outputs/sign_weight/factor_add2_adj_07_f18_decay30_industry_metrics.csv` | Migrated from the `main` branch `group_work/factor_add_new/` experiment into the formal `FACTOR_REGISTRY`. Formula: industry-ranked f18 decay variant with 30-day VROC decay. |
| `factor_add2_adj_04_f34_10_30_industry` | `factor_add2_adj_04_f34_10_30_industry` | screened_addon | pass; AR 11.87%, SR 2.006, ICIR 1.870, coverage 0.938; metrics: `group_work/02_factor_calculation/outputs/sign_weight/factor_add2_adj_04_f34_10_30_industry_metrics.csv` | Migrated from the `main` branch `group_work/factor_add_new/` experiment into the formal `FACTOR_REGISTRY`. Formula: industry-ranked f34 variant with 10-day close-rank volatility and 30-day VROC covariance. |
| `factor_add3_gap_down_3` | `factor_add3_gap_down_3` | screened_addon | pass; AR 49.71%, SR 3.251, ICIR 2.947, coverage 1.000; metrics: `group_work/02_factor_calculation/outputs/sign_weight/factor_add3_gap_down_3_metrics.csv` | Added for the low-correlation target. Formula: 3-day sum of negative overnight gap events. |
| `factor_add3_overnight_reversal_3_industry_inv` | `factor_add3_overnight_reversal_3_industry_inv` | screened_addon | pass; AR 15.15%, SR 2.643, ICIR 2.696, coverage 0.947; metrics: `group_work/02_factor_calculation/outputs/sign_weight/factor_add3_overnight_reversal_3_industry_inv_metrics.csv` | Added for the low-correlation target. Direction-adjusted industry-ranked 3-day overnight-return signal. |
| `factor_add3_intraday_hml_vol_120_industry_inv` | `factor_add3_intraday_hml_vol_120_industry_inv` | screened_addon | pass; AR 18.57%, SR 2.605, ICIR 2.724, coverage 1.000; metrics: `group_work/02_factor_calculation/outputs/sign_weight/factor_add3_intraday_hml_vol_120_industry_inv_metrics.csv` | Added for the low-correlation target. Direction-adjusted industry-ranked spread between upside and downside intraday volatility. |
| `factor_add3_amihud_illiq_10_industry` | `factor_add3_amihud_illiq_10_industry` | screened_addon | pass; AR 22.21%, SR 2.108, ICIR 2.304, coverage 0.944; metrics: `group_work/02_factor_calculation/outputs/sign_weight/factor_add3_amihud_illiq_10_industry_metrics.csv` | Added for the low-correlation target. Formula: industry-ranked 10-day Amihud-style illiquidity. |
| `factor_add3_turnover_weighted_reversal_20_industry` | `factor_add3_turnover_weighted_reversal_20_industry` | screened_addon | pass; AR 20.17%, SR 2.123, ICIR 2.360, coverage 0.938; metrics: `group_work/02_factor_calculation/outputs/sign_weight/factor_add3_turnover_weighted_reversal_20_industry_metrics.csv` | Added for the low-correlation target. Direction-adjusted industry-ranked 20-day turnover-weighted return reversal. |
| `factor_add3_f18_decay90_industry` | `factor_add3_f18_decay90_industry` | screened_addon | pass; AR 15.96%, SR 2.094, ICIR 2.175, coverage 0.949; metrics: `group_work/02_factor_calculation/outputs/sign_weight/factor_add3_f18_decay90_industry_metrics.csv` | Added for the low-correlation target. Industry-ranked f18 variant with slower 90-day VROC decay. |

## AR/SR-Qualified Stage-2 Deliverables

All rows below use the formal evaluator with `sign_weight`, `delay=2`, `listed_days=20`, and `start_date=2017-01-01`.

Base command pattern:

```powershell
conda run -n bishe python group_work\02_factor_calculation\evaluate_factor.py --factor <factor_key> --ls-method sign_weight
```

| Registry key | Construction | AR | SR | ICIR | Coverage | Metrics | Reproduce command |
|---|---|---:|---:|---:|---:|---|---|
| `factor_add_06_quality_x_flow` | `pn_Rank(NetProfitTTMQ1 / NetAssetQ1) * pn_Rank(ts_Sum(net_mf_amount, 20))` | 16.25% | 2.008 | 1.797 | 0.917 | `group_work/02_factor_calculation/outputs/sign_weight/factor_add_06_quality_x_flow_metrics.csv` | `conda run -n bishe python group_work\02_factor_calculation\evaluate_factor.py --factor factor_add_06_quality_x_flow --ls-method sign_weight` |
| `factor_opt_01_residual_volatility_w5` | `factor_01_residual_volatility(window=5)` | 32.67% | 2.881 | 2.899 | 1.000 | `group_work/02_factor_calculation/outputs/sign_weight/factor_opt_01_residual_volatility_w5_metrics.csv` | `conda run -n bishe python group_work\02_factor_calculation\evaluate_factor.py --factor factor_opt_01_residual_volatility_w5 --ls-method sign_weight` |
| `factor_opt_01_residual_volatility_w10` | `factor_01_residual_volatility(window=10)` | 30.15% | 2.536 | 2.500 | 1.000 | `group_work/02_factor_calculation/outputs/sign_weight/factor_opt_01_residual_volatility_w10_metrics.csv` | `conda run -n bishe python group_work\02_factor_calculation\evaluate_factor.py --factor factor_opt_01_residual_volatility_w10 --ls-method sign_weight` |
| `factor_opt_05_volume_price_divergence_cov_1_20` | `factor_05_volume_price_divergence_cov(delta_window=1, cov_window=20)` | 26.64% | 2.104 | 2.057 | 1.000 | `group_work/02_factor_calculation/outputs/sign_weight/factor_opt_05_volume_price_divergence_cov_1_20_metrics.csv` | `conda run -n bishe python group_work\02_factor_calculation\evaluate_factor.py --factor factor_opt_05_volume_price_divergence_cov_1_20 --ls-method sign_weight` |
| `factor_opt_07_price_volume_deviation_vol_w15` | `factor_07_price_volume_deviation_vol(window=15)` | 33.25% | 2.128 | 2.046 | 0.946 | `group_work/02_factor_calculation/outputs/sign_weight/factor_opt_07_price_volume_deviation_vol_w15_metrics.csv` | `conda run -n bishe python group_work\02_factor_calculation\evaluate_factor.py --factor factor_opt_07_price_volume_deviation_vol_w15 --ls-method sign_weight` |
| `factor_opt_13_main_fund_stability_w5` | `factor_13_main_fund_stability(window=5)` | 29.08% | 2.001 | 1.961 | 0.947 | `group_work/02_factor_calculation/outputs/sign_weight/factor_opt_13_main_fund_stability_w5_metrics.csv` | `conda run -n bishe python group_work\02_factor_calculation\evaluate_factor.py --factor factor_opt_13_main_fund_stability_w5 --ls-method sign_weight` |
| `factor_opt_33_reinstatement_residual_vol_ratio_40_20` | `factor_33_reinstatement_residual_vol_ratio(reinstatement_window=40, stdev_window=20)` | 17.13% | 2.553 | 3.018 | 1.000 | `group_work/02_factor_calculation/outputs/sign_weight/factor_opt_33_reinstatement_residual_vol_ratio_40_20_metrics.csv` | `conda run -n bishe python group_work\02_factor_calculation\evaluate_factor.py --factor factor_opt_33_reinstatement_residual_vol_ratio_40_20 --ls-method sign_weight` |
| `factor_opt_33_reinstatement_residual_vol_ratio_80_20` | `factor_33_reinstatement_residual_vol_ratio(reinstatement_window=80, stdev_window=20)` | 16.53% | 2.614 | 3.038 | 1.000 | `group_work/02_factor_calculation/outputs/sign_weight/factor_opt_33_reinstatement_residual_vol_ratio_80_20_metrics.csv` | `conda run -n bishe python group_work\02_factor_calculation\evaluate_factor.py --factor factor_opt_33_reinstatement_residual_vol_ratio_80_20 --ls-method sign_weight` |
| `factor_opt_34_reverse_vroc_rank_vol_cov_5_20` | `factor_34_reverse_vroc_rank_vol_cov(rank_vol_window=5, cov_window=20)` | 16.82% | 2.345 | 2.312 | 0.940 | `group_work/02_factor_calculation/outputs/sign_weight/factor_opt_34_reverse_vroc_rank_vol_cov_5_20_metrics.csv` | `conda run -n bishe python group_work\02_factor_calculation\evaluate_factor.py --factor factor_opt_34_reverse_vroc_rank_vol_cov_5_20 --ls-method sign_weight` |
| `factor_opt_47_nonlinear_volume_price_extreme_reversal_30_30_5` | `factor_47_nonlinear_volume_price_extreme_reversal(poly_window=30, kurt_window=30, kurt_top_window=5)` | 19.04% | 2.132 | 2.333 | 0.943 | `group_work/02_factor_calculation/outputs/sign_weight/factor_opt_47_nonlinear_volume_price_extreme_reversal_30_30_5_metrics.csv` | `conda run -n bishe python group_work\02_factor_calculation\evaluate_factor.py --factor factor_opt_47_nonlinear_volume_price_extreme_reversal_30_30_5 --ls-method sign_weight` |
| `factor_opt_54_industry_fund_quality_reverse_inv` | `-factor_54_industry_fund_quality_reverse()` | 10.75% | 2.085 | 2.029 | 0.944 | `group_work/02_factor_calculation/outputs/sign_weight/factor_opt_54_industry_fund_quality_reverse_inv_metrics.csv` | `conda run -n bishe python group_work\02_factor_calculation\evaluate_factor.py --factor factor_opt_54_industry_fund_quality_reverse_inv --ls-method sign_weight` |
| `factor_add2_adj_05_f34_15_25_industry` | `pn_GroupRank(factor_34_reverse_vroc_rank_vol_cov(rank_vol_window=15, cov_window=25), hy)` | 11.56% | 2.026 | 1.939 | 0.940 | `group_work/02_factor_calculation/outputs/sign_weight/factor_add2_adj_05_f34_15_25_industry_metrics.csv` | `conda run -n bishe python group_work\02_factor_calculation\evaluate_factor.py --factor factor_add2_adj_05_f34_15_25_industry --ls-method sign_weight` |
| `factor_add2_adj_07_f18_decay30_industry` | `pn_GroupRank(factor_18_price_volume_decay_synergy(rank_window=10, vroc_window=12, decay_window=30), hy)` | 15.28% | 2.007 | 2.173 | 0.949 | `group_work/02_factor_calculation/outputs/sign_weight/factor_add2_adj_07_f18_decay30_industry_metrics.csv` | `conda run -n bishe python group_work\02_factor_calculation\evaluate_factor.py --factor factor_add2_adj_07_f18_decay30_industry --ls-method sign_weight` |
| `factor_add2_adj_04_f34_10_30_industry` | `pn_GroupRank(factor_34_reverse_vroc_rank_vol_cov(rank_vol_window=10, cov_window=30), hy)` | 11.87% | 2.006 | 1.870 | 0.938 | `group_work/02_factor_calculation/outputs/sign_weight/factor_add2_adj_04_f34_10_30_industry_metrics.csv` | `conda run -n bishe python group_work\02_factor_calculation\evaluate_factor.py --factor factor_add2_adj_04_f34_10_30_industry --ls-method sign_weight` |
| `factor_add3_gap_down_3` | `3-day sum of negative overnight gap events` | 49.71% | 3.251 | 2.947 | 1.000 | `group_work/02_factor_calculation/outputs/sign_weight/factor_add3_gap_down_3_metrics.csv` | `conda run -n bishe python group_work\02_factor_calculation\evaluate_factor.py --factor factor_add3_gap_down_3 --ls-method sign_weight` |
| `factor_add3_overnight_reversal_3_industry_inv` | `-pn_GroupRank(-ts_Mean(overnightRet, 3), hy)` | 15.15% | 2.643 | 2.696 | 0.947 | `group_work/02_factor_calculation/outputs/sign_weight/factor_add3_overnight_reversal_3_industry_inv_metrics.csv` | `conda run -n bishe python group_work\02_factor_calculation\evaluate_factor.py --factor factor_add3_overnight_reversal_3_industry_inv --ls-method sign_weight` |
| `factor_add3_intraday_hml_vol_120_industry_inv` | `-pn_GroupRank(ts_Stdev(adj_high / delay(adj_close) - 1, 120) - ts_Stdev(adj_low / delay(adj_close) - 1, 120), hy)` | 18.57% | 2.605 | 2.724 | 1.000 | `group_work/02_factor_calculation/outputs/sign_weight/factor_add3_intraday_hml_vol_120_industry_inv_metrics.csv` | `conda run -n bishe python group_work\02_factor_calculation\evaluate_factor.py --factor factor_add3_intraday_hml_vol_120_industry_inv --ls-method sign_weight` |
| `factor_add3_amihud_illiq_10_industry` | `pn_GroupRank(ts_Mean(abs(totalRet) / amount, 10), hy)` | 22.21% | 2.108 | 2.304 | 0.944 | `group_work/02_factor_calculation/outputs/sign_weight/factor_add3_amihud_illiq_10_industry_metrics.csv` | `conda run -n bishe python group_work\02_factor_calculation\evaluate_factor.py --factor factor_add3_amihud_illiq_10_industry --ls-method sign_weight` |
| `factor_add3_turnover_weighted_reversal_20_industry` | `-pn_GroupRank(ts_Sum(totalRet * turnover_rate, 20) / ts_Sum(turnover_rate, 20), hy)` | 20.17% | 2.123 | 2.360 | 0.938 | `group_work/02_factor_calculation/outputs/sign_weight/factor_add3_turnover_weighted_reversal_20_industry_metrics.csv` | `conda run -n bishe python group_work\02_factor_calculation\evaluate_factor.py --factor factor_add3_turnover_weighted_reversal_20_industry --ls-method sign_weight` |
| `factor_add3_f18_decay90_industry` | `pn_GroupRank(factor_18_price_volume_decay_synergy(rank_window=10, vroc_window=12, decay_window=90), hy)` | 15.96% | 2.094 | 2.175 | 0.949 | `group_work/02_factor_calculation/outputs/sign_weight/factor_add3_f18_decay90_industry_metrics.csv` | `conda run -n bishe python group_work\02_factor_calculation\evaluate_factor.py --factor factor_add3_f18_decay90_industry --ls-method sign_weight` |

## Correlation Check

Run command:

```powershell
conda run -n bishe python group_work\02_factor_calculation\screening_results\calc_corr_14_passed.py
```

Result on 2026-05-24: 20 AR/SR-qualified factors, 156 / 190 pairs with `abs(corr) < 0.3`, and maximum all-pairs-low-correlation subset size 11. Outputs:

- `group_work/02_factor_calculation/screening_results/corr_20_passed_factors.csv`
- `group_work/02_factor_calculation/screening_results/abs_corr_20_passed_factors.csv`
- `group_work/02_factor_calculation/screening_results/corr_pairs_20_passed_factors.csv`
- `group_work/02_factor_calculation/screening_results/max_low_corr_sets_20_passed_factors.csv`

## Work Log

- 2026-05-21: Read `AGENTS_zh.md`, `mission_zh.md`, project guide, formulas, custom operators, runtime operators, factor implementations, data loader, evaluator, and this progress file.
- 2026-05-21: Confirmed 56 source markdown files and 36 pre-existing registered factor keys before new edits.
- 2026-05-21: Added lazy local field loading in `group_work/factor_lib/factors.py` for matrix/finMatrix fields used by proxy factors, including computed `vwap`.
- 2026-05-21: Added reusable operators to both `code/stock1800/feature.py` and `group_work/01_feature_engineering/custom_operators.py`: `Sin`, `pn_CSPct`, `pn_CSSkew`, `pn_GroupRank`, `pn_GroupStdev`, `Winsorize`, `ts_TopKSum`, `ts_MaxMean`, `ts_MaxStd`, `ts_MinDiff`, and `ts_AvDiff`.
- 2026-05-21: Implemented and registered source IDs `11`, `18`, `20`, `23`, `24`, `25`, `27`, `29`, `30`, `32`, `33`, `34`, `45`, `46`, `47`, `51`, `53`, `54`, and `55`.
- 2026-05-21: Classified source ID `21` as `missing_unsolved` because `REINSTATEMENT_CHG_60D` has no credible local equivalent. Kept ID `26` as `missing_unsolved` for current local validation because the registered Barra implementation has 0.0 latest coverage after alignment.
- 2026-05-21: Ran `py_compile` for `factors.py`, `feature.py`, and `custom_operators.py`; passed. Conda emitted non-blocking `conda-libmamba-solver` entry-point warnings.
- 2026-05-21: Ran evaluator for all 55 registered factor keys; all passed and wrote metrics/daily-return/cumret outputs under `group_work/02_factor_calculation/outputs/`.
- 2026-05-23: Migrated screened factor `factor_add_06_quality_x_flow` into `group_work/factor_lib/factors.py`, documented it in `factor_formulas.md`, and validated it with `evaluate_factor.py --factor factor_add_06_quality_x_flow --ls-method sign_weight`.
- 2026-05-23: Registered 10 optimized stage-2 variants as `factor_opt_*` wrapper keys in `group_work/factor_lib/factors.py` so each target factor can be reproduced by a normal `evaluate_factor.py --factor <key>` command.
- 2026-05-23: Ran `py_compile` for `factors.py`, `feature.py`, `custom_operators.py`, and `evaluate_factor.py`; passed.
- 2026-05-23: Validated all 10 optimized keys in one `bishe` Python process via `evaluate_factor(...)` and `save_outputs(...)`; all meet AR > 10% and SR > 2 under `sign_weight`.
- 2026-05-23: Migrated 3 `factor_add2_*` industry-neutral add-on factors from the `main` branch `group_work/factor_add_new/` experiment into `group_work/factor_lib/factors.py`, documented them, and validated each with `evaluate_factor.py --ls-method sign_weight`; all meet AR > 10% and SR > 2.
- 2026-05-23: Added `group_work/02_factor_calculation/screening_results/calc_corr_14_passed.py` for the 14 AR/SR-qualified factors, wrote `corr_14_passed_factors.csv`, `abs_corr_14_passed_factors.csv`, and `corr_pairs_14_passed_factors.csv`; 69 of 91 pairs have `abs(corr) < 0.3`.
- 2026-05-24: Screened low-correlation candidate families covering gap, overnight, intraday volatility spread, Amihud illiquidity, turnover-weighted reversal, and slower f18 decay; selected 6 `factor_add3_*` keys for formal registration.
- 2026-05-24: Validated all 6 `factor_add3_*` keys with `evaluate_factor.py --ls-method sign_weight`; all meet AR > 10% and SR > 2.
- 2026-05-24: Expanded `calc_corr_14_passed.py` to the 20 AR/SR-qualified keys and added maximum low-correlation set output; current result finds an 11-factor subset with pairwise `abs(corr) < 0.3`.
