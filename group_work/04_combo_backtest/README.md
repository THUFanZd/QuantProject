# 第四阶段：组合因子构建与回测

本目录是第四阶段独立工作包：将冻结的 10 个入选因子合成为组合因子，控制 Barra 风格和行业暴露，并输出相对中证1000的持仓回测结果。文件提交清单见 `FILE_MANIFEST.md`。

## 方法

主结果采用仅使用历史已实现 IC 的滚动 `IC_IR` 加权：

```text
combo_t = sum((rolling_IC_IR_i,t / sum(abs(rolling_IC_IR_t))) * standardized_factor_i,t)
```

`combo_backtest.py` 按如下步骤执行：

1. 从本目录 `inputs/selected_factors.csv` 读取冻结的最终 10 个因子，并从 `inputs/factor_quality_summary.csv` 读取指标快照。
2. 支持 `equal`、`ic`、`ic_ir` 三种组合方式；`ic` / `ic_ir` 在每个信号日仅使用已经实现的历史 IC 估计动态权重。
3. 调用 `FACTOR_REGISTRY` 重新计算并标准化因子，沿用上市满 20 日和中证1000成分股掩码。
4. 对组合因子做逐日截面回归，剔除 10 个 Barra 风格因子和行业哑变量暴露。
5. 将中性化残差转成主动多空权重，并叠加到 `idxWgt` 指数基准权重上。
6. 动态限制主动覆盖层，保证增强组合最终持仓非负且每日权重和为 1。
7. 使用延迟 2 个交易日的持仓计算收益，输出组合净值、超额收益和风险指标。
8. 输出组合因子中性化前后的风格、行业暴露对比以及月度胜率。

当前默认 `IC_IR` 权重采用 252 个历史可观测 IC 的滚动窗口，并要求至少 252 个历史观测后才启动主动持仓；因而不会使用未来区间的 IC/IC_IR 决定当期组合权重。

## 运行

在仓库根目录执行：

```bash
python group_work/04_combo_backtest/combo_backtest.py \
  --data-root "/Users/songyufei/Desktop/量化课件/量化4:29/课程资料（中证1000）/stock1000/data" \
  --weight-method ic_ir
```

在课程原 Windows 环境中，也可以通过 `TS_DAILY_DATA_ROOT` 设置数据目录后直接运行。

## 目录结构

```text
04_combo_backtest/
├── combo_backtest.py
├── barra_support.py
├── README.md
├── FILE_MANIFEST.md
├── inputs/
│   ├── selected_factors.csv
│   └── factor_quality_summary.csv
└── outputs/
    └── 回测报告、曲线、指标表、暴露对比与持仓明细
```

本目录仍调用仓库共享的 `group_work/factor_lib/` 与 `code/stock1800/feature.py`，并在运行时读取课程原始数据；这些是整个项目共用依赖，不重复复制进第四阶段文件夹。

## 输出

运行后结果保存在 `outputs/`：

- `combo_factor_weights.csv`：组合因子权重。
- `combo_metrics.csv`：年化收益、超额 Sharpe、最大回撤、月度胜率等指标。
- `combo_daily_returns.csv`：组合、基准、超额及中性多空日收益和净值。
- `combo_monthly_returns.csv`：月度收益与超额收益胜负记录。
- `combo_factor_weights_timeseries.csv`：每日历史滚动组合权重。
- `combo_observable_ic_timeseries.csv`：每个信号日可使用的历史 IC。
- `combo_style_exposure.csv`：中性化前后的风格暴露检查。
- `combo_industry_signal_exposure.csv`：组合因子中性化前后的行业暴露检查。
- `combo_industry_active_exposure.csv`：主动组合行业偏离时间序列。
- `combo_latest_holdings.csv`：末日组合持仓。
- `combo_nav_vs_benchmark.png`：组合净值与中证1000对比曲线。
- `combo_excess_nav.png`：超额净值与中性多空净值曲线。
- `combo_backtest_report_zh.md`：可直接整合进作业报告的阶段总结。
