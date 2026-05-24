# calc_corr_14_passed.py 说明

`calc_corr_14_passed.py` 是第二阶段相关性检查脚本，用来计算当前 AR/SR 过线因子之间的日截面平均相关系数，并输出两两低相关的最大因子集合。文件名保留了最初 14 因子版本的名字，但当前脚本已扩展到 20 个因子。

## 计算对象

脚本统一从 `group_work.factor_lib.factors.FACTOR_REGISTRY` 读取因子，不再依赖单独的 `factor_add_new` 实验目录。

20 个因子包括：

1. `factor_add_06_quality_x_flow`
2. 10 个 `factor_opt_*` 参数优化版因子
3. 3 个 `factor_add2_*` 行业中性增强因子
4. 6 个 `factor_add3_*` 低相关补充因子

## 计算口径

```text
原始因子值 -> 指数样本/上市天数过滤 -> pn_TransNorm -> 逐日截面相关系数 -> 时间平均
```

默认上市天数过滤为 `listed_days=20`，低相关组合统计阈值为 `abs(corr) < 0.3`。

脚本默认将标准化后的因子分数缓存到 `archive/root_scratch/corr14_score_cache/`。该目录在 `.gitignore` 覆盖范围内，用于长任务中断后的续跑；如果要强制重算，增加 `--refresh-cache`。

## 运行方式

在项目根目录运行：

```powershell
python group_work\02_factor_calculation\screening_results\calc_corr_14_passed.py
```

可选参数：

```powershell
python group_work\02_factor_calculation\screening_results\calc_corr_14_passed.py --listed-days 20 --threshold 0.3
python group_work\02_factor_calculation\screening_results\calc_corr_14_passed.py --refresh-cache
```

## 输出文件

默认输出到 `group_work/02_factor_calculation/screening_results/`：

| 文件 | 说明 |
|---|---|
| `corr_20_passed_factors.csv` | 20 个因子的相关系数矩阵 |
| `abs_corr_20_passed_factors.csv` | 20 个因子的相关系数绝对值矩阵 |
| `corr_pairs_20_passed_factors.csv` | 两两相关性展开排序表 |
| `max_low_corr_sets_20_passed_factors.csv` | 最大两两 `abs(corr) < 0.3` 因子集合 |

2026-05-24 复跑结果：20 个 AR/SR 过线因子中，156 / 190 组满足 `abs(corr) < 0.3`，最大可抽出 11 个因子满足任意两两 `abs(corr) < 0.3`。

## 当前 11 因子低相关集合

`max_low_corr_sets_20_passed_factors.csv` 中输出了 8 组并列的 11 因子最大集合。它们的共同核心是：

1. `factor_add3_overnight_reversal_3_industry_inv`
2. `factor_opt_54_industry_fund_quality_reverse_inv`
3. `factor_opt_47_nonlinear_volume_price_extreme_reversal_30_30_5`
4. `factor_add3_gap_down_3`
5. `factor_add3_intraday_hml_vol_120_industry_inv`
6. `factor_add_06_quality_x_flow`
7. `factor_add3_f18_decay90_industry`
8. `factor_add3_turnover_weighted_reversal_20_industry`

另外 3 个位置来自三组替代项，任选其一后仍可组成 11 因子低相关集合：

1. `factor_add2_adj_04_f34_10_30_industry` 或 `factor_add2_adj_05_f34_15_25_industry`
2. `factor_opt_33_reinstatement_residual_vol_ratio_40_20` 或 `factor_opt_33_reinstatement_residual_vol_ratio_80_20`
3. `factor_add3_amihud_illiq_10_industry` 或 `factor_opt_13_main_fund_stability_w5`

如果需要引用一个明确的 11 因子版本，可以使用结果文件第一行：

1. `factor_add3_overnight_reversal_3_industry_inv`
2. `factor_opt_54_industry_fund_quality_reverse_inv`
3. `factor_opt_47_nonlinear_volume_price_extreme_reversal_30_30_5`
4. `factor_add3_gap_down_3`
5. `factor_add3_intraday_hml_vol_120_industry_inv`
6. `factor_add_06_quality_x_flow`
7. `factor_add3_f18_decay90_industry`
8. `factor_add2_adj_04_f34_10_30_industry`
9. `factor_opt_33_reinstatement_residual_vol_ratio_80_20`
10. `factor_add3_turnover_weighted_reversal_20_industry`
11. `factor_add3_amihud_illiq_10_industry`

## 推荐优先使用的 10 个因子

如果最终只选 10 个使用，建议优先使用下面这一组：

1. `factor_add3_gap_down_3`
2. `factor_opt_13_main_fund_stability_w5`
3. `factor_add3_turnover_weighted_reversal_20_industry`
4. `factor_opt_47_nonlinear_volume_price_extreme_reversal_30_30_5`
5. `factor_add3_intraday_hml_vol_120_industry_inv`
6. `factor_opt_33_reinstatement_residual_vol_ratio_40_20`
7. `factor_add_06_quality_x_flow`
8. `factor_add3_f18_decay90_industry`
9. `factor_add3_overnight_reversal_3_industry_inv`
10. `factor_add2_adj_05_f34_15_25_industry`

这组因子两两仍满足 `abs(corr) < 0.3`。取舍逻辑是：在 11 因子最大集合的基础上，优先保留 AR、SR、IC 表现更均衡的版本；`factor_opt_33_reinstatement_residual_vol_ratio_40_20` 相比 `80_20` 的 AR/IC 略高，`factor_add2_adj_05_f34_15_25_industry` 相比 `04` 的 SR/ICIR 略好；`factor_opt_13_main_fund_stability_w5` 相比 `factor_add3_amihud_illiq_10_industry` 的 AR 和 IC 更高。被剔除的是 `factor_opt_54_industry_fund_quality_reverse_inv`，主要因为它在当前 11 因子候选中的 AR 和 IC 相对最低；如果更看重极低相关性和行业质量维度的分散，可以把它作为备选补回。
