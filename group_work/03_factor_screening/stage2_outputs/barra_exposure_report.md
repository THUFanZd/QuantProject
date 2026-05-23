# Stage 2 Barra Exposure Diagnostics

- Source metrics: `group_work\03_factor_screening\stage2_outputs\factor_metrics_all.csv`
- Style exposure lag: `1` trading day(s)
- Portfolio weight delay: `2` trading day(s)
- Style proxy flag: `top_corr_abs_mean >= 0.30`

## What This Adds

This report checks whether a Stage 2 factor is mostly a known Barra style exposure.
It does not change the existing Stage 2 selection result.

## Highest Style-Likeness Factors

| Factor | Top style | Mean abs corr | P95 abs corr | Top portfolio style | Mean abs portfolio exposure | Flag |
|---|---|---:|---:|---|---:|---|
| `factor_04_reversal_turnover_enhanced` | Growth | 0.117 | 0.263 | Beta | 0.224 | no |
| `factor_15_multi_dimensional_reversal` | Growth | 0.111 | 0.238 | Beta | 0.232 | no |
| `factor_12_turnover_volatility` | Growth | 0.107 | 0.243 | Beta | 0.209 | no |
| `factor_44_volume_divergence_composite_momentum` | Growth | 0.099 | 0.219 | Beta | 0.205 | no |
| `factor_03_turnover_volatility_momentum` | Growth | 0.092 | 0.229 | Beta | 0.181 | no |
| `factor_13_main_fund_stability` | Liquidity | 0.079 | 0.198 | Beta | 0.158 | no |
| `factor_07_price_volume_deviation_vol` | Liquidity | 0.074 | 0.187 | Beta | 0.143 | no |
| `factor_19_price_momentum_fund_volatility_reverse` | Liquidity | 0.071 | 0.189 | Beta | 0.140 | no |
| `factor_05_volume_price_divergence_cov` | Liquidity | 0.068 | 0.190 | Beta | 0.124 | no |
| `factor_01_residual_volatility` | Liquidity | 0.064 | 0.165 | Beta | 0.119 | no |

## Flagged Factors

No factor crossed the configured style-proxy threshold.
