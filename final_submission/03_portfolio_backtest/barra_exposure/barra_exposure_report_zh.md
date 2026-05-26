# 第三阶段 Barra 风格暴露分析报告

## 分析口径

- 数据环境：`C:\ts_daily\stock1000\data`
- 分析区间：`2017-01-01` 至 `2026-03-23`
- 股票池：中证1000成分股，使用 `idxWgt.csv` 屏蔽非成分股，并要求上市满20个交易日
- 因子处理：原始因子 -> 股票池/上市天数过滤 -> `pn_TransNorm` 截面标准化
- 风格暴露：10个 Barra CNE5 风格因子，使用 `shift(1)` 避免前视偏差
- 行业暴露：使用 `hy.pkl` 的申万2021一级行业编码，映射为中文行业名称后计算各行业内因子均值
- Barra 回归：逐日截面回归 `factor = alpha + 10 styles + industry dummies + residual`

## 10个有效因子及第二阶段表现

| factor | stage2_ar | stage2_sr | stage2_ic_mean | stage2_ic_ir | latest_coverage |
| --- | --- | --- | --- | --- | --- |
| factor_add3_gap_down_3 | 0.4971 | 3.2514 | 0.0113 | 2.9471 | 1.0000 |
| factor_opt_13_main_fund_stability_w5 | 0.2908 | 2.0010 | 0.0173 | 1.9613 | 0.9470 |
| factor_add3_turnover_weighted_reversal_20_industry | 0.2017 | 2.1225 | 0.0136 | 2.3605 | 0.9380 |
| factor_opt_47_nonlinear_volume_price_extreme_reversal_30_30_5 | 0.1904 | 2.1317 | 0.0127 | 2.3326 | 0.9430 |
| factor_add3_intraday_hml_vol_120_industry_inv | 0.1857 | 2.6054 | 0.0117 | 2.7238 | 0.9990 |
| factor_opt_33_reinstatement_residual_vol_ratio_40_20 | 0.1713 | 2.5525 | 0.0122 | 3.0183 | 1.0000 |
| factor_add_06_quality_x_flow | 0.1625 | 2.0081 | 0.0093 | 1.7967 | 0.9170 |
| factor_add3_f18_decay90_industry | 0.1596 | 2.0939 | 0.0101 | 2.1753 | 0.9490 |
| factor_add3_overnight_reversal_3_industry_inv | 0.1515 | 2.6429 | 0.0095 | 2.6956 | 0.9470 |
| factor_add2_adj_05_f34_15_25_industry | 0.1156 | 2.0258 | 0.0070 | 1.9394 | 0.9400 |

## 10因子 x 10风格暴露矩阵

矩阵元素为 2017 年以来逐日截面相关系数的时间均值。

| factor_key | Size | Beta | Momentum | ResVol | NLS | BTP | Liquidity | EY | Growth | Leverage |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| factor_add3_gap_down_3 | 0.0064 | -0.0065 | -0.0127 | -0.0555 | 0.0074 | 0.0318 | -0.0815 | 0.0250 | -0.0012 | 0.0010 |
| factor_opt_13_main_fund_stability_w5 | -0.4484 | -0.2368 | -0.3252 | -0.1114 | -0.4304 | 0.2754 | -0.5448 | 0.0664 | -0.0698 | 0.0164 |
| factor_add3_turnover_weighted_reversal_20_industry | -0.0814 | -0.0083 | 0.0428 | -0.0234 | -0.0786 | 0.0648 | -0.1251 | 0.0182 | -0.0150 | 0.0024 |
| factor_opt_47_nonlinear_volume_price_extreme_reversal_30_30_5 | 0.0060 | -0.1134 | 0.0492 | 0.0342 | 0.0036 | -0.1081 | -0.1775 | 0.0075 | 0.1015 | -0.0821 |
| factor_add3_intraday_hml_vol_120_industry_inv | -0.0673 | -0.1298 | -0.1824 | -0.1099 | -0.0659 | 0.1354 | -0.3176 | 0.0954 | 0.0248 | 0.0028 |
| factor_opt_33_reinstatement_residual_vol_ratio_40_20 | -0.1732 | 0.1162 | -0.0518 | -0.0223 | -0.1686 | 0.0537 | -0.1657 | 0.0082 | -0.0191 | -0.0186 |
| factor_add_06_quality_x_flow | -0.0373 | -0.1666 | -0.1133 | -0.0687 | -0.0354 | 0.0505 | -0.3397 | 0.0643 | 0.0432 | -0.0069 |
| factor_add3_f18_decay90_industry | 0.0474 | 0.0201 | -0.0003 | -0.0780 | 0.0437 | 0.0635 | -0.1767 | 0.0836 | 0.0495 | -0.0125 |
| factor_add3_overnight_reversal_3_industry_inv | 0.0151 | 0.0157 | -0.0169 | -0.0639 | 0.0140 | 0.0240 | -0.1237 | 0.0319 | 0.0138 | -0.0041 |
| factor_add2_adj_05_f34_15_25_industry | -0.0086 | -0.0161 | -0.0222 | -0.0472 | -0.0075 | 0.0377 | -0.1278 | 0.0256 | 0.0155 | 0.0015 |

## 主要风格暴露说明

阈值设为 `|corr| > 0.4`。

| factor | main_style_exposure | max_abs_style_corr |
| --- | --- | --- |
| factor_add3_gap_down_3 | 无显著单一风格暴露(|corr|<=0.4) | 0.0815 |
| factor_opt_13_main_fund_stability_w5 | Liquidity-0.54; Size-0.45; NLS-0.43 | 0.5448 |
| factor_add3_turnover_weighted_reversal_20_industry | 无显著单一风格暴露(|corr|<=0.4) | 0.1251 |
| factor_opt_47_nonlinear_volume_price_extreme_reversal_30_30_5 | 无显著单一风格暴露(|corr|<=0.4) | 0.1775 |
| factor_add3_intraday_hml_vol_120_industry_inv | 无显著单一风格暴露(|corr|<=0.4) | 0.3176 |
| factor_opt_33_reinstatement_residual_vol_ratio_40_20 | 无显著单一风格暴露(|corr|<=0.4) | 0.1732 |
| factor_add_06_quality_x_flow | 无显著单一风格暴露(|corr|<=0.4) | 0.3397 |
| factor_add3_f18_decay90_industry | 无显著单一风格暴露(|corr|<=0.4) | 0.1767 |
| factor_add3_overnight_reversal_3_industry_inv | 无显著单一风格暴露(|corr|<=0.4) | 0.1237 |
| factor_add2_adj_05_f34_15_25_industry | 无显著单一风格暴露(|corr|<=0.4) | 0.1278 |

## Barra 纯 Alpha 比例

`mean_r2` 越高，说明因子越容易被 Barra 风格和行业解释；`pure_alpha_ratio = 1 - mean_r2` 越高，说明纯 Alpha 成分越强。

| factor | mean_r2 | pure_alpha_ratio | alpha_class | main_style_exposure |
| --- | --- | --- | --- | --- |
| factor_opt_13_main_fund_stability_w5 | 0.5725 | 0.4275 | Alpha/风格混合 | Liquidity-0.54; Size-0.45; NLS-0.43 |
| factor_add3_intraday_hml_vol_120_industry_inv | 0.2469 | 0.7531 | Alpha主导 | 无显著单一风格暴露(|corr|<=0.4) |
| factor_add_06_quality_x_flow | 0.2271 | 0.7729 | Alpha主导 | 无显著单一风格暴露(|corr|<=0.4) |
| factor_opt_47_nonlinear_volume_price_extreme_reversal_30_30_5 | 0.2259 | 0.7741 | Alpha主导 | 无显著单一风格暴露(|corr|<=0.4) |
| factor_opt_33_reinstatement_residual_vol_ratio_40_20 | 0.1871 | 0.8129 | Alpha主导 | 无显著单一风格暴露(|corr|<=0.4) |
| factor_add3_turnover_weighted_reversal_20_industry | 0.1575 | 0.8425 | Alpha主导 | 无显著单一风格暴露(|corr|<=0.4) |
| factor_add3_f18_decay90_industry | 0.1514 | 0.8486 | Alpha主导 | 无显著单一风格暴露(|corr|<=0.4) |
| factor_add3_gap_down_3 | 0.0911 | 0.9089 | Alpha主导 | 无显著单一风格暴露(|corr|<=0.4) |
| factor_add3_overnight_reversal_3_industry_inv | 0.0864 | 0.9136 | Alpha主导 | 无显著单一风格暴露(|corr|<=0.4) |
| factor_add2_adj_05_f34_15_25_industry | 0.0760 | 0.9240 | Alpha主导 | 无显著单一风格暴露(|corr|<=0.4) |

## 行业暴露摘要

`industry_dispersion` 为各行业平均暴露的标准差，用来衡量行业偏离强弱。

| factor | industry_dispersion | top_abs_industry | top_abs_industry_exposure |
| --- | --- | --- | --- |
| factor_add3_turnover_weighted_reversal_20_industry | 0.4873 | 银行(801780) | -2.3853 |
| factor_add3_overnight_reversal_3_industry_inv | 0.4831 | 银行(801780) | -2.3932 |
| factor_add3_f18_decay90_industry | 0.4496 | 银行(801780) | 2.1312 |
| factor_add2_adj_05_f34_15_25_industry | 0.4463 | 银行(801780) | 2.1311 |
| factor_add3_intraday_hml_vol_120_industry_inv | 0.4425 | 银行(801780) | -2.4014 |
| factor_opt_13_main_fund_stability_w5 | 0.2899 | 纺织服饰(801130) | 0.7250 |
| factor_add_06_quality_x_flow | 0.2149 | 钢铁(801040) | 0.4294 |
| factor_opt_33_reinstatement_residual_vol_ratio_40_20 | 0.1877 | 综合(801230) | -0.7008 |
| factor_opt_47_nonlinear_volume_price_extreme_reversal_30_30_5 | 0.1599 | 纺织服饰(801130) | 0.3792 |
| factor_add3_gap_down_3 | 0.0164 | 有色金属(801050) | -0.0762 |

## 中性化前后对比

这里的中性化因子取 Barra 回归残差。若 `post_max_abs_style_corr` 和 `post_industry_dispersion` 明显下降，说明 Barra 风格和行业暴露得到了有效压制。

| factor | pre_max_abs_style_corr | post_max_abs_style_corr | pre_industry_dispersion | post_industry_dispersion |
| --- | --- | --- | --- | --- |
| factor_opt_13_main_fund_stability_w5 | 0.5448 | 0.0000 | 0.2899 | 0.0000 |
| factor_add_06_quality_x_flow | 0.3397 | 0.0000 | 0.2149 | 0.0000 |
| factor_add3_intraday_hml_vol_120_industry_inv | 0.3176 | 0.0000 | 0.4425 | 0.0000 |
| factor_opt_47_nonlinear_volume_price_extreme_reversal_30_30_5 | 0.1775 | 0.0000 | 0.1599 | 0.0000 |
| factor_add3_f18_decay90_industry | 0.1767 | 0.0000 | 0.4496 | 0.0000 |
| factor_opt_33_reinstatement_residual_vol_ratio_40_20 | 0.1732 | 0.0000 | 0.1877 | 0.0000 |
| factor_add2_adj_05_f34_15_25_industry | 0.1278 | 0.0000 | 0.4463 | 0.0000 |
| factor_add3_turnover_weighted_reversal_20_industry | 0.1251 | 0.0000 | 0.4873 | 0.0000 |
| factor_add3_overnight_reversal_3_industry_inv | 0.1237 | 0.0000 | 0.4831 | 0.0000 |
| factor_add3_gap_down_3 | 0.0815 | 0.0006 | 0.0164 | 0.0000 |

## 结论

本阶段产出显示，10个有效因子整体可以进一步拆分为 Alpha 主导、Alpha/风格混合、以及风格或行业驱动三类。后续第四阶段构建组合因子时，建议优先使用 Barra 回归残差或至少对组合因子进行行业和风格中性化，以降低 Size、Liquidity、ResVol 等常见风险因子的重复暴露。

## 输出文件

- `style_exposure_matrix.csv` / `style_exposure_heatmap.png`
- `main_style_exposures.csv`
- `industry_code_map.csv`
- `industry_exposure_matrix.csv` / `industry_exposure_heatmap.png`
- `barra_regression_summary.csv`
- `neutralization_compare.csv`
- `style_exposure_matrix_neutralized.csv` / `style_exposure_heatmap_neutralized.png`
- `industry_exposure_matrix_neutralized.csv` / `industry_exposure_heatmap_neutralized.png`
- `barra_regression_r2_timeseries.csv`
- `barra_regression_alpha_timeseries.csv`
- `barra_regression_nobs_timeseries.csv`
