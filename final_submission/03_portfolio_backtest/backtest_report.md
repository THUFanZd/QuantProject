# 第四阶段：组合因子构建与回测

## 实现口径

- 入选因子：`inputs/selected_factors.csv` 中冻结的 10 个低相关达标因子。
- 合成方法：滚动历史 `IC_IR` 加权；主结果默认使用 `IC_IR` 加权。
- 防前视权重：每个信号日仅使用当日已实现且可观测的历史 IC，滚动窗口 `252` 个交易日、最少 `252` 个观测；不读取未来时期的因子表现决定当期权重。
- 中性化：逐日截面回归剔除 10 个 Barra 风格暴露和申万一级行业哑变量，主动信号取回归残差。
- 持仓：以中证1000 `idxWgt` 为基准，叠加中性主动权重；主动覆盖比例上限为 `20.00%`，并动态收缩以确保最终持仓非负且权重和为 1。
- 回测：信号与收益间延迟 `2` 个交易日，风格暴露使用上一交易日数据，单边成本率 `0.0000%`。

## 组合权重

| factor_key | stage2_ic_ir | latest_combo_weight | mean_abs_combo_weight |
| --- | --- | --- | --- |
| factor_add3_gap_down_3 | 2.9471 | 12.51% | 11.28% |
| factor_opt_13_main_fund_stability_w5 | 1.9613 | 7.36% | 8.21% |
| factor_add3_turnover_weighted_reversal_20_industry | 2.3605 | 6.29% | 10.18% |
| factor_opt_47_nonlinear_volume_price_extreme_reversal_30_30_5 | 2.3326 | 12.52% | 9.61% |
| factor_add3_intraday_hml_vol_120_industry_inv | 2.7238 | 9.32% | 12.21% |
| factor_opt_33_reinstatement_residual_vol_ratio_40_20 | 3.0183 | 17.50% | 12.58% |
| factor_add_06_quality_x_flow | 1.7967 | 13.93% | 7.29% |
| factor_add3_f18_decay90_industry | 2.1753 | 10.88% | 8.95% |
| factor_add3_overnight_reversal_3_industry_inv | 2.6956 | 2.26% | 12.14% |
| factor_add2_adj_05_f34_15_25_industry | 1.9394 | 7.43% | 7.55% |

## 回测结果

| 指标 | 结果 |
| --- | ---: |
| 回测区间 | 2018-01-17 至 2026-03-23 |
| 组合年化收益 | 11.41% |
| 中证1000年化收益 | 10.36% |
| 年化超额收益 | 1.05% |
| 超额 Sharpe | 3.457 |
| 超额最大回撤 | -0.35% |
| 超额月度胜率 | 82.83%（82/99） |
| 中性多空年化收益 | 22.50% |
| 中性多空 Sharpe | 3.755 |

## 中性化检查

组合信号在中性化前后的 Barra 风格截面相关均值如下。中性化后残差用于构建主动持仓。

| style | pre_neutral_signal_corr | post_neutral_signal_corr |
| --- | --- | --- |
| Size | -0.1510 | 0.0000 |
| Beta | -0.0636 | 0.0000 |
| Momentum | -0.1009 | 0.0000 |
| ResVol | -0.1143 | -0.0000 |
| NLS | -0.1466 | 0.0000 |
| BTP | 0.1324 | -0.0000 |
| Liquidity | -0.4264 | 0.0000 |
| EY | 0.0921 | -0.0000 |
| Growth | 0.0338 | 0.0000 |
| Leverage | -0.0235 | -0.0000 |

行业均值暴露离散度由 `0.2756` 降至 `0.0000`。以下展示中性化前绝对暴露最大的 10 个行业：

| industry | pre_neutral_signal_mean | post_neutral_signal_mean |
| --- | --- | --- |
| 银行(801780) | -1.1232 | 0.0000 |
| 综合(801230) | -0.8615 | -0.0000 |
| 非银金融(801790) | -0.2898 | 0.0000 |
| 纺织服饰(801130) | 0.2352 | -0.0000 |
| 美容护理(801980) | -0.2349 | 0.0000 |
| 交通运输(801170) | 0.2008 | 0.0000 |
| 煤炭(801950) | -0.1857 | 0.0000 |
| 轻工制造(801140) | 0.1757 | -0.0000 |
| 有色金属(801050) | -0.1412 | -0.0000 |
| 建筑材料(801710) | -0.1091 | 0.0000 |

## 输出文件

- `combo_factor_weights.csv`：10 个因子及其组合权重。
- `combo_metrics.csv`：回测核心指标。
- `combo_daily_returns.csv`：日收益和净值序列。
- `combo_monthly_returns.csv`：月度收益和超额胜负记录。
- `combo_style_exposure.csv`：组合中性化前后的风格暴露。
- `combo_industry_signal_exposure.csv`：组合中性化前后的行业暴露对比。
- `combo_industry_active_exposure.csv`：中性主动组合每日行业权重偏离。
- `combo_factor_weights_timeseries.csv`：严格历史口径下每日组合权重。
- `combo_observable_ic_timeseries.csv`：权重估计可使用的历史 IC 序列。
- `combo_latest_holdings.csv`：末日实际持仓。
- `combo_nav_vs_benchmark.png`：组合与中证1000净值对比。
- `combo_excess_nav.png`：超额收益与中性多空净值曲线。
