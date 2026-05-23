# factor_add_2_recalc 说明

本目录用于补充 3 个已通过 `AR > 10%`、`SR > 2` 筛选的行业中性增强因子，并计算它们与现有过线因子的相关性。

## 因子脚本

`factor_add_2_recalc.py` 中定义了 3 个因子：

| 因子名 | 公式说明 | 使用字段 |
|---|---|---|
| `factor_add2_adj_05_f34_15_25_industry` | `pn_GroupRank(-ts_Cov(ts_ChgRate(vol, 12), ts_Stdev(pn_Rank(close), 15), 25), hy)` | `close`, `vol`, `hy` |
| `factor_add2_adj_07_f18_decay30_industry` | `pn_GroupRank(-ts_Percentage(pn_Rank(close), 10) * ts_Decay(ts_ChgRate(vol, 12), 30), hy)` | `close`, `vol`, `hy` |
| `factor_add2_adj_04_f34_10_30_industry` | `pn_GroupRank(-ts_Cov(ts_ChgRate(vol, 12), ts_Stdev(pn_Rank(close), 10), 30), hy)` | `close`, `vol`, `hy` |

其中 `pn_GroupRank(..., hy)` 表示按行业做截面排名，用来降低行业暴露并增强因子稳定性。

## 相关性计算

`calc_corr_14_passed.py` 会将这 3 个因子与更新版项目中已有的 11 个 AR/SR 过线因子合并，计算 14 个因子之间的日截面平均相关系数。

运行方式：

```powershell
python group_work\factor_add_2_recalc\calc_corr_14_passed.py
```

输出文件位于：

```text
group_work/factor_add_2_recalc/outputs/
```

主要输出：

- `corr_14_passed_factors.csv`：14 个因子的相关系数矩阵
- `abs_corr_14_passed_factors.csv`：相关系数绝对值矩阵
- `corr_pairs_14_passed_factors.csv`：两两相关性排序表

## 筛选结果

这 3 个因子此前在 `evaluate_factor.py + FACTOR_REGISTRY + pn_TransNorm` 口径下测试通过：

| 因子名 | 年化收益率 AR | 夏普 SR |
|---|---:|---:|
| `factor_add2_adj_05_f34_15_25_industry` | 11.56% | 2.03 |
| `factor_add2_adj_07_f18_decay30_industry` | 15.28% | 2.01 |
| `factor_add2_adj_04_f34_10_30_industry` | 11.87% | 2.01 |
