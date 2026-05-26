# 第四阶段文件清单

本目录是“组合因子构建与回测”阶段的完整工作包，包含固定输入快照、实现代码和回测产出。推送本文件夹时请包含下列文件。

## 代码与说明

| 文件 | 用途 |
| --- | --- |
| `combo_backtest.py` | 主程序：动态组合因子、Barra/行业中性化、指数增强回测和结果输出 |
| `barra_support.py` | 本阶段使用的数据对齐、Barra 风格读取和截面回归中性化辅助函数 |
| `README.md` | 方法、运行方式和输出说明 |
| `.gitignore` | 排除 macOS 与 Python 缓存文件 |

## 固定输入快照

| 文件 | 用途 |
| --- | --- |
| `inputs/selected_factors.csv` | 第四阶段使用的 10 个入选因子名单 |
| `inputs/factor_quality_summary.csv` | 组合构建中用于核验因子表现的第二阶段指标快照 |

## 结果输出

| 文件 | 用途 |
| --- | --- |
| `outputs/combo_backtest_report_zh.md` | 第四阶段文字报告 |
| `outputs/combo_nav_vs_benchmark.png` | 组合净值与中证1000净值对比图 |
| `outputs/combo_excess_nav.png` | 超额净值与中性多空净值曲线图 |
| `outputs/combo_metrics.csv` | 回测指标汇总表 |
| `outputs/combo_daily_returns.csv` | 日收益与日净值序列 |
| `outputs/combo_monthly_returns.csv` | 月度收益与月度胜负记录 |
| `outputs/combo_factor_weights.csv` | 10 个因子的组合权重摘要 |
| `outputs/combo_factor_weights_timeseries.csv` | 滚动历史组合权重序列 |
| `outputs/combo_observable_ic_timeseries.csv` | 当期可观察到的历史 IC 序列 |
| `outputs/combo_style_exposure.csv` | 组合风格中性化前后对比 |
| `outputs/combo_industry_signal_exposure.csv` | 组合行业中性化前后对比 |
| `outputs/combo_industry_active_exposure.csv` | 中性主动持仓的每日行业偏离 |
| `outputs/combo_latest_holdings.csv` | 最后交易日的实际组合持仓 |
| `outputs/combo_regression_diagnostics.csv` | Barra 回归诊断时间序列 |

## 仓库共享依赖

本目录不会复制以下项目公共代码和原始数据。将本目录推送到现有项目分支后，运行仍需要它们存在：

- `group_work/factor_lib/`：候选因子注册与实现。
- `code/stock1800/feature.py`：基础算子与多空持仓构造。
- 中证1000课程原始数据目录：运行时通过 `--data-root` 或 `TS_DAILY_DATA_ROOT` 提供。
