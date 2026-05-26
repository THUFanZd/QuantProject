# 第二阶段：因子筛选结果

## 计算口径

- 回测区间：`2017-01-01` 起，数据实际结束于 `2026-03-23`。
- 可交易性处理：中证1000成分股掩码、上市满 20 日掩码、异常日收益 `abs(totalRet) > 0.2` 置为空。
- 防未来函数：因子持仓使用 `shift(2)` 后的收益计算。
- 截面处理：因子值采用 `pn_TransNorm` 标准化后构建多空组合。
- 达标条件：`|AR| > 10%`、`|SR| > 2`，最终 10 个因子两两 `|corr| < 0.3`。

## 最终入选因子

| 因子键 | AR | SR | IC Mean | IC IR |
| --- | ---: | ---: | ---: | ---: |
| `factor_add3_gap_down_3` | 49.71% | 3.251 | 0.0113 | 2.947 |
| `factor_opt_13_main_fund_stability_w5` | 29.08% | 2.001 | 0.0173 | 1.961 |
| `factor_add3_turnover_weighted_reversal_20_industry` | 20.17% | 2.123 | 0.0136 | 2.360 |
| `factor_opt_47_nonlinear_volume_price_extreme_reversal_30_30_5` | 19.04% | 2.132 | 0.0127 | 2.333 |
| `factor_add3_intraday_hml_vol_120_industry_inv` | 18.57% | 2.605 | 0.0117 | 2.724 |
| `factor_opt_33_reinstatement_residual_vol_ratio_40_20` | 17.13% | 2.553 | 0.0122 | 3.018 |
| `factor_add_06_quality_x_flow` | 16.25% | 2.008 | 0.0093 | 1.797 |
| `factor_add3_f18_decay90_industry` | 15.96% | 2.094 | 0.0101 | 2.175 |
| `factor_add3_overnight_reversal_3_industry_inv` | 15.15% | 2.643 | 0.0095 | 2.696 |
| `factor_add2_adj_05_f34_15_25_industry` | 11.56% | 2.026 | 0.0070 | 1.939 |

## 相关性检验

从 20 个 AR/SR 达标候选中选择以上 10 个因子。基于逐日截面相关均值矩阵，入选因子的最大两两绝对相关系数为 `0.277369`，小于课程要求阈值 `0.3`。对应热图见 `corr_matrix.png`，原始数值见 `support/corr_20_passed_factors.csv`。

## 复现命令

```bash
python final_submission/02_factor_calculation/batch_compute.py --selected-only
python final_submission/02_factor_calculation/batch_compute.py --plot-only
```

不传入 `--selected-only` 时，`batch_compute.py` 默认批量评估注册表内的全部候选因子，满足课程对批量计算脚本和至少 20 个候选因子的要求。
