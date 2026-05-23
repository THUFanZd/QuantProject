# factor_add_2_recalc.py 说明

`factor_add_2_recalc.py` 是 3 个新增过线因子的定义脚本，只负责因子计算，不负责回测和相关性统计。

## 包含因子

| 因子名 | 公式说明 | 使用字段 |
|---|---|---|
| `factor_add2_adj_05_f34_15_25_industry` | `pn_GroupRank(-ts_Cov(ts_ChgRate(vol, 12), ts_Stdev(pn_Rank(close), 15), 25), hy)` | `close`, `vol`, `hy` |
| `factor_add2_adj_07_f18_decay30_industry` | `pn_GroupRank(-ts_Percentage(pn_Rank(close), 10) * ts_Decay(ts_ChgRate(vol, 12), 30), hy)` | `close`, `vol`, `hy` |
| `factor_add2_adj_04_f34_10_30_industry` | `pn_GroupRank(-ts_Cov(ts_ChgRate(vol, 12), ts_Stdev(pn_Rank(close), 10), 30), hy)` | `close`, `vol`, `hy` |

## 设计思路

这 3 个因子都来自量价类因子的行业中性增强版本：

- `f34` 类因子使用成交量变化率与价格截面排名波动率的滚动协方差；
- `f18` 类因子使用价格截面位置与成交量变化率衰减项的组合；
- 外层统一使用 `pn_GroupRank(..., hy)` 做行业内排名，降低行业暴露。

## 筛选结果

这 3 个因子此前在 `evaluate_factor.py + FACTOR_REGISTRY + pn_TransNorm` 口径下测试通过：

| 因子名 | 年化收益率 AR | 夏普 SR |
|---|---:|---:|
| `factor_add2_adj_05_f34_15_25_industry` | 11.56% | 2.03 |
| `factor_add2_adj_07_f18_decay30_industry` | 15.28% | 2.01 |
| `factor_add2_adj_04_f34_10_30_industry` | 11.87% | 2.01 |
