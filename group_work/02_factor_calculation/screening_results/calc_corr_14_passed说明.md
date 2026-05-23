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
