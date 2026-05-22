# `try1_param_search.py` 说明

## 1. 脚本来源

`try1_param_search.py` 是在项目已有正式回测口径 `evaluate_factor.py + FACTOR_REGISTRY + pn_TransNorm` 的基础上整理出来的轻量参数搜索脚本。

最开始直接使用项目已有单因子 metrics 时，严格按照 `AR > 10%`、`SR > 2` 只能筛出少数达标因子；同时有一些因子收益率已经较高，但夏普比率接近 2。为了在不改变正式回测框架的前提下提升这些候选因子的稳定性，我们对接近达标的因子做了小范围窗口参数搜索。

## 2. 脚本作用

该脚本用于对指定候选因子进行批量参数搜索，并输出统一的评价指标汇总表。

本次搜索的候选因子包括：

- `factor_47_nonlinear_volume_price_extreme_reversal`
- `factor_13_main_fund_stability`
- `factor_05_volume_price_divergence_cov`
- `factor_43_turnover_relative_strength_reversal`
- `factor_19_price_momentum_fund_volatility_reverse`
- `factor_34_reverse_vroc_rank_vol_cov`
- `factor_15_multi_dimensional_reversal`
- `factor_52_large_outflow_momentum_reversal`

每个因子最多测试 5 组参数组合。脚本只输出汇总 CSV，不为每个因子单独生成 Excel 或详细图表，因此运行和复核更轻量。

## 3. 回测口径

本脚本保持当前项目正式单因子评价口径：

- 因子来源：`FACTOR_REGISTRY`
- 标准化方式：`pn_TransNorm`
- 多空组合：沿用 `feature.get_ls_post`
- 调仓延迟：`delay = 2`
- 新股过滤：`listed_days = 20`
- 回测起始日期：`2017-01-01`
- 极端收益过滤：`abs(totalRet) > 0.2` 记为缺失
- 允许方向取反：若原始 `ls_sr < 0`，则记录反向后的 `selected_ar`、`selected_sr`

最终筛选标准为：

```text
selected_ar > 10%
selected_sr > 2
```

## 4. 输出文件

脚本输出文件为：

```text
group_work/02_factor_calculation/outputs_try1/factor_metrics_all_try1.csv
```

其中主要字段包括：

- `factor`：因子名称
- `variant`：参数组合编号
- `params`：参数设置
- `direction`：是否取反，`1` 表示原方向，`-1` 表示反向
- `selected_ar`：方向调整后的年化收益率
- `selected_sr`：方向调整后的夏普比率
- `selected_ic_mean`：方向调整后的 IC 均值
- `selected_ic_ir`：方向调整后的 ICIR
- `latest_coverage`：最新一期覆盖率

## 5. 本次主要结果

本次参数搜索中，严格满足 `AR > 10%`、`SR > 2` 的主要结果包括：

| 因子 | 最优参数 | AR | SR |
|---|---|---:|---:|
| `factor_34_reverse_vroc_rank_vol_cov` | `rank_vol_window=5, cov_window=20` | 16.82% | 2.35 |
| `factor_47_nonlinear_volume_price_extreme_reversal` | `poly_window=30, kurt_window=30, kurt_top_window=5` | 19.04% | 2.13 |
| `factor_05_volume_price_divergence_cov` | `delta_window=1, cov_window=20` | 26.64% | 2.10 |
| `factor_13_main_fund_stability` | `window=5` | 29.08% | 2.00 |

其中，最终第二阶段核心 5 个达标低相关因子采用了：

- `factor_33_reinstatement_residual_vol_ratio`
- `factor_54_industry_fund_quality_reverse` 反向
- `factor_13_main_fund_stability(window=5)`
- `factor_34_reverse_vroc_rank_vol_cov(rank_vol_window=5, cov_window=20)`
- `factor_47_nonlinear_volume_price_extreme_reversal(poly_window=30, kurt_window=30, kurt_top_window=5)`

`try1_param_search.py` 的主要贡献是为 `factor_13`、`factor_34`、`factor_47` 找到了更优参数组合，使其在正式口径下满足第二阶段的收益率和夏普比率要求。
