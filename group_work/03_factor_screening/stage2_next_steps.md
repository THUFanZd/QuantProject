# Stage 2 Next Steps

## 1. Standardization

The current batch script standardizes each raw factor cross-sectionally before portfolio construction and correlation analysis:

- raw factor -> universe/listed mask
- cross-sectional z-score standardization by date
- long-short weights from the standardized factor
- IC and factor correlation from standardized factor values

Implementation: `stage2_screen_factors.py`, `pn_trans_norm()` and `evaluate_one()`.

## 2. Strict Factors

Using `AR > 10%` and `SR > 2` as strict filters, there are currently 8 factors:

| Factor | AR | SR | ICIR |
|---|---:|---:|---:|
| `factor_04_reversal_turnover_enhanced` | 63.64% | 2.91 | 2.66 |
| `factor_07_price_volume_deviation_vol` | 47.66% | 2.44 | 2.33 |
| `factor_12_turnover_volatility` | 41.86% | 2.26 | 1.97 |
| `factor_13_main_fund_stability` | 42.08% | 2.25 | 2.15 |
| `factor_01_residual_volatility` | 34.66% | 2.17 | 2.12 |
| `factor_03_turnover_volatility_momentum` | 33.19% | 2.10 | 1.95 |
| `factor_05_volume_price_divergence_cov` | 36.89% | 2.08 | 2.07 |
| `factor_44_volume_divergence_composite_momentum` | 32.87% | 2.05 | 1.95 |

## 3. Two Candidate Adjustments

Parameter search suggests two practical ways to add factors that pass `AR > 10%` and `SR > 2`.

### Candidate A: turnover relative-strength reversal, short/long = 5/180

Formula:

```python
-safe_div(ts_Mean(turnover, 5), ts_Mean(turnover, 180))
```

Metrics:

- AR: 42.07%
- SR: 2.52
- IC mean: 0.0213
- ICIR: 2.50

This is an adjusted version of factor 43. The original 20/120 version had SR 1.90; using 5/180 strengthens the short-term turnover overheating reversal signal.

### Candidate B: price momentum and fund-flow volatility, lag/window = 5/15

Formula:

```python
-pn_Rank(adj_close / ts_Delay(adj_close, 5)) * pn_Rank(ts_Stdev(net_mf_amount, 15))
```

Metrics:

- AR: 30.55%
- SR: 2.16
- IC mean: 0.0200
- ICIR: 2.32

This is an adjusted version of factor 19. The original 15/15 version had SR 1.93; shortening the price momentum leg to 5 trading days improves the reversal timing.

## 4. Correlation And Orthogonalization

The strict 8 raw factors are highly correlated:

- max average cross-sectional absolute correlation: 0.845
- mean average cross-sectional absolute correlation: 0.515

Adding Candidate A and Candidate B gives 10 strict-return candidates, but raw correlations remain high:

- max average cross-sectional absolute correlation: 0.845
- mean average cross-sectional absolute correlation: 0.485

Sequential daily cross-sectional orthogonalization can reduce correlations to almost zero, but it also removes most of the alpha:

- raw max/mean abs corr: 0.845 / 0.485
- orthogonalized max/mean abs corr: approximately 0 / 0
- after orthogonalization, only the first factor keeps SR above 2; most residual factors fall below SR 1.1

Conclusion: orthogonalization solves the correlation matrix mechanically, but for this factor set it is too aggressive if each residualized factor still needs to pass standalone `SR > 2`.

## 5. Recommended Plan

Use raw factors to satisfy the strict return filter, then handle correlation in the combination stage rather than forcing each single factor to be fully residualized.

Recommended strict 10:

1. `factor_04_reversal_turnover_enhanced`
2. `factor_43v_turnover_relative_strength_reversal_5_180`
3. `factor_07_price_volume_deviation_vol`
4. `factor_12_turnover_volatility`
5. `factor_13_main_fund_stability`
6. `factor_01_residual_volatility`
7. `factor_15v_multi_dimensional_reversal_10_10_15` or `factor_19v_price_momentum_fund_volatility_reverse_5_15`
8. `factor_03_turnover_volatility_momentum`
9. `factor_05_volume_price_divergence_cov`
10. `factor_44_volume_divergence_composite_momentum`

For the final combined factor, use one of these:

- cluster highly correlated factors and equal-weight within clusters first, then equal-weight clusters;
- or apply mild orthogonalization only to the composite factor inputs, while reporting the raw strict factor performance separately;
- or replace several turnover/low-volatility factors with more independent fundamental or capital-flow candidates before final submission.

