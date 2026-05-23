# calc_corr_14_passed.py 说明

`calc_corr_14_passed.py` 是相关性计算脚本，用来计算 14 个 AR/SR 过线因子之间的日截面平均相关系数。

## 计算对象

脚本包含两类因子：

1. 更新版项目中已经注册到 `FACTOR_REGISTRY` 的 11 个 AR/SR 过线因子；
2. `factor_add_2_recalc.py` 中重新定义的 3 个新增过线因子。

共计 14 个因子。

## 计算口径

每个因子先按大作业口径处理：

```text
原始因子值 -> 指数样本/上市天数过滤 -> pn_TransNorm -> 日截面相关系数
```

最终相关系数为逐日截面相关系数的时间平均值。

## 运行方式

在项目根目录运行：

```powershell
python group_work\factor_add_2_recalc\calc_corr_14_passed.py
```

## 输出文件

结果输出到：

```text
group_work/factor_add_2_recalc/outputs/
```

主要文件：

| 文件 | 说明 |
|---|---|
| `corr_14_passed_factors.csv` | 14 个因子的相关系数矩阵 |
| `abs_corr_14_passed_factors.csv` | 14 个因子的相关系数绝对值矩阵 |
| `corr_pairs_14_passed_factors.csv` | 两两相关性展开排序表 |

## 当前结果摘要

14 个因子共 91 组两两组合，其中 `abs(corr) < 0.3` 的组合有 69 组。

可选出的最大低相关因子集合包含 7 个因子：

```text
factor_add_06_quality_x_flow
factor_opt_01_residual_volatility_w5
factor_opt_33_reinstatement_residual_vol_ratio_40_20
factor_opt_47_nonlinear_volume_price_extreme_reversal_30_30_5
factor_opt_54_industry_fund_quality_reverse_inv
factor_add2_adj_05_f34_15_25_industry
factor_add2_adj_07_f18_decay30_industry
```
