# Factor Formula List

本文件为第一阶段「特征工程与算子实现」提交物之一。  
我们从知乎「实战因子365」系列中整理因子公式，并将原始表达式映射为本地可运行的 `dt[...] + feature.py` 算子形式。

## Status 说明

- **ready**：字段基本完全匹配，可以直接进入因子计算。
- **proxy**：原文字段本地不存在，使用本地近似字段或简化逻辑替代。
- **no**：字段缺失严重、数据覆盖率差，或实现复杂度过高，暂不进入第二阶段主筛选。

---

| Factor ID | Factor Name | Source | Formula | Required Fields | Status | Evaluation Results | Notes |
|---|---|---|---|---|---|---|---|
| 01 | 残差波动率因子 | `实战因子365_cleaned/【实战因子365】01.残差波动率因子(IC 0.0524,sharpe 1.9964).md` | `-ts_Stdev(pn_CrossResidual(dt["close"], dt["vol"]), 20)` | `close`, `vol` | **ready** | 待测试 | 原文 `CS_REGRESSION(CLOSE, VOLUME, OUT_TYPE=0)` 映射为 `pn_CrossResidual(dt["close"], dt["vol"])`，再计算20日残差波动率。 |
| 02 | 量价效率因子 | `实战因子365_cleaned/【实战因子365】02.量价效率因子(IC 0.0356,sharpe 1.5714).md` | `safe_div(pn_Rank(ts_Sum(dt["vol"], 30)), pn_Rank(ts_Sum(dt["amount"], 30)))` | `vol`, `amount` | **ready** | 待测试 | 原文为30日成交量排名 / 30日成交额排名，用于刻画量价相对效率。 |
| 03 | 换手率波动动量因子 | `实战因子365_cleaned/【实战因子365】03.换手率波动动量因子(IC 0.0570,sharpe 1.5603).md` | `-SignedPower(pn_Rank(ts_Stdev(safe_div(dt["vol"] * 100, dt["float_share"]), 14)), 2) * ts_Rank(dt["close"], 30)` | `vol`, `float_share`, `close` | **proxy** | 待测试 | 原文使用 `TURN_RATE`，本地用 `vol * 100 / float_share` 代理换手率。 |
| 04 | 反转换手增强因子 | `实战因子365_cleaned/【实战因子365】04.反转换手增强因子(IC 0.0596,sharpe 1.6999).md` | `-safe_div(dt["adj_close"], ts_Delay(dt["adj_close"], 5)) * safe_div(dt["vol"] * 100, dt["float_share"])` | `adj_close`, `vol`, `float_share` | **proxy** | 待测试 | 原文使用 `AF_CLOSE` 与 `TURN_RATE`，本地用前复权收盘价和构造换手率替代。 |
| 05 | 量价背离协动因子 | `实战因子365_cleaned/【实战因子365】05.量价背离协动因子(IC 0.0511,sharpe 1.6598).md` | `-ts_Cov(ts_Delta(dt["vol"], 1), ts_Delta(dt["close"], 1), 30)` | `vol`, `close` | **ready** | **AR: 25.2%, SR: 1.92, ICIR: 1.82** ⭐ | 原文 `VOLUME` 映射为本地成交量 `vol`，计算量价变动协方差并取负。 |
| 06 | 均线过滤反转因子 | `实战因子365_cleaned/【实战因子365】06.均线过滤反转因子(IC 0.0273,sharpe 1.8766).md` | `-(ts_Delta(dt["close"], 10)).where(dt["close"] > ts_Sum(dt["close"], 35) / 35, 0)` | `close` | **ready** | **AR: 18.2%, SR: 1.45, ICIR: 1.25** | 当收盘价高于35日均线时返回负10日价格变化，否则返回0，捕捉均线突破后的短期反转。 |
| 07 | 价量偏离波动率因子 | `实战因子365_cleaned/【实战因子365】07.价量偏离波动率因子(IC 0.0610,sharpe 1.9919).md` | `-ts_Stdev((dt["close"] - dt["vwap"]) * dt["vol"], 10)` | `close`, `vwap`, `vol` | **ready** | 待测试 | 原文为 `-TS_STDDEV((CLOSE - VWAP) * VOLUME, 10)`，字段可直接映射。 |
| 08 | 流动性稳定度因子 | `实战因子365_cleaned/【实战因子365】08.流动性稳定度因子(IC 0.0500,sharpe 1.9711).md` | `-ts_Mean(pn_Rank(dt["amount"]), 10)` | `amount` | **ready** | **AR: 21.7%, SR: 1.24, ICIR: 1.06** | `RANK` 使用每日截面百分位排名，取10日成交额排名均值的负值。 |
| 09 | 波动调整反转因子 | `实战因子365_cleaned/【实战因子365】09.波动调整反转因子(IC 0.0469,sharpe 1.8654).md` | `-ts_Mean(SignedPower(dt["totalRet"], 2), 30)` | `totalRet` | **ready** | 待测试 | 原文 `CHANGE_PCT` 映射为本地 `totalRet`，带符号平方后计算30日均值并取负。 |
| 10 | 偏离度成交量加权因子 | `实战因子365_cleaned/【实战因子365】10.偏离度成交量加权因子(IC 0.0365,sharpe 1.7458).md` | `(ts_Mean(dt["close"], 20) - dt["close"]) * pn_Rank(dt["vol"])` | `close`, `vol` | **ready** | 待测试 | 20日均线偏离度 × 成交量截面排名，捕捉放量条件下的均值回归。 |
| 12 | 换手率波动因子 | `实战因子365_cleaned/【实战因子365】12.换手率波动因子(IC 0.0554,sharpe 1.8977).md` | `-ts_Stdev(safe_div(dt["vol"] * 100, dt["float_share"]), 15)` | `vol`, `float_share` | **proxy** | 待测试 | 原文使用 `TURN_RATE`，本地用 `vol * 100 / float_share` 代理。 |
| 13 | 主力资金稳定性因子 | `实战因子365_cleaned/【实战因子365】13.主力资金稳定性因子(IC 0.0525,sharpe 1.9096).md` | `-ts_Stdev(dt["net_mf_amount"], 10)` | `net_mf_amount` | **proxy** | **AR: 29.7%, SR: 1.97, ICIR: 1.92** ⭐ | 原文 `MAIN_IN_FLOW_V2` 映射为本地 `net_mf_amount`，计算10日主力资金流波动率并取负。 |
| 14 | 主力资金流入峰值逆向排序因子 | `实战因子365_cleaned/【实战因子365】14.主力资金流入峰值逆向排序因子(IC 0.0502,sharpe 1.9168).md` | `-pn_Rank(ts_Max(dt["net_mf_amount"], 10))` | `net_mf_amount` | **proxy** | 待测试 | 原文使用 `MAIN_IN_FLOW_V2`，本地用 `net_mf_amount` 替代。 |
| 15 | 多维度反转因子 | `实战因子365_cleaned/【实战因子365】15.多维度反转因子(IC 0.0474,sharpe 1.7302).md` | `-pn_Rank(safe_div(dt["close"], ts_Mean(dt["close"], 20))) * pn_Rank(ts_Mean(dt["vol"], 20)) * pn_Rank(ts_Mean(safe_div(dt["vol"] * 100, dt["float_share"]), 20))` | `close`, `vol`, `float_share` | **proxy** | 待测试 | 原文同时使用价格相对强度、成交量均值和换手率均值；换手率由本地字段代理。 |
| 16 | 量价协同波动负向选股因子 | `实战因子365_cleaned/【实战因子365】16.量价协同波动负向选股因子(IC 0.0552,sharpe 1.8847).md` | `-pn_Rank(ts_Stdev(dt["close"], 10)) * pn_Rank(ts_Stdev(dt["vol"], 10))` | `close`, `vol` | **ready** | 待测试 | 价格波动率排名与成交量波动率排名相乘后取负，偏好量价波动双低股票。 |
| 17 | 双维度波动率负向协同因子 | `实战因子365_cleaned/【实战因子365】17.双维度波动率负向协同因子(IC 0.0585,sharpe 1.8693).md` | `-pn_Rank(ts_Stdev(dt["close"], 10)) * pn_Rank(ts_Stdev(dt["net_mf_amount"], 10))` | `close`, `net_mf_amount` | **proxy** | 待测试 | 原文使用价格波动率和主力资金流波动率，本地用 `net_mf_amount` 代理资金流。 |
| 19 | 价格动量与主力资金流波动率逆向耦合因子 | `实战因子365_cleaned/【实战因子365】19.价格动量与主力资金流波动率逆向耦合因子(IC 0.0514,sharpe 1.8525).md` | `-pn_Rank(safe_div(dt["adj_close"], ts_Delay(dt["adj_close"], 15))) * pn_Rank(ts_Stdev(dt["net_mf_amount"], 15))` | `adj_close`, `net_mf_amount` | **proxy** | 待测试 | 原文 `MAIN_IN_FLOW_V2` 用 `net_mf_amount` 代理，构建价格动量与资金流波动率的反向耦合。 |
| 22 | 动量反转因子 | `实战因子365_cleaned/【实战因子365】22.动量反转因子(IC 0.0399,sharpe 1.6168).md` | `-ts_Sum(ts_Delta(pn_Rank(dt["adj_close"]), 1), 40)` | `adj_close` | **ready** | 待测试 | 对复权收盘价做截面排名，计算排名日度差分后40日累计并取负。 |
| 26 | 双风格IR利差因子 | `实战因子365_cleaned/【实战因子365】26.双风格IR利差因子(IC 0.0369,sharpe 1.9701).md` | `ts_IR(dt["Beta"], 20) - ts_IR(dt["Size"], 20)` | `Beta`, `Size` | **no** | AR: 0.2%, SR: 0.04, ICIR: -0.04 ⚠️ | Barra数据日期范围与股票数据不完全对齐，最新日期覆盖率为0%，暂不进入第二阶段主筛选。 |
| 28 | 主力与超大单协同流入强度因子 | `实战因子365_cleaned/【实战因子365】28.主力与超大单协同流入强度因子(IC 0.0303,sharpe 1.9837).md` | `pn_Rank(ts_Percentage(ts_Sum(dt["net_mf_amount"], 20), 30) * ts_Decay(dt["buy_elg_vol"] - dt["sell_elg_vol"], 15))` | `net_mf_amount`, `buy_elg_vol`, `sell_elg_vol` | **proxy** | 待测试 | 原文使用主力资金和超大单资金流，本地用 `net_mf_amount` 与超大单买卖量差值代理。 |
| 31 | 资金流入动量因子 | `实战因子365_cleaned/【实战因子365】31.资金流入动量因子(IC 0.0369,sharpe 1.9963).md` | `ts_Decay(Abs(pn_Rank(ts_Sum(dt["net_mf_amount"], 20))) - Abs(pn_Rank(dt["buy_elg_vol"] - dt["sell_elg_vol"])), 15)` | `net_mf_amount`, `buy_elg_vol`, `sell_elg_vol` | **proxy** | 待测试 | 原文为主力资金与超大单资金流向强度差，本地使用资金流与超大单净流入代理。 |
| 35 | 价差动量因子 | `实战因子365_cleaned/【实战因子365】35.价差动量因子(IC 0.0347,sharpe 1.9148).md` | `(ts_Mean(dt["open"], 10) - ts_Mean(dt["close"], 10)) * pn_Rank(ts_Delta(dt["close"], 10))` | `open`, `close` | **ready** | **AR: 15.4%, SR: 1.28, ICIR: 1.31** | 原文 `RANK` 映射为 `pn_Rank`，用于刻画开收盘价差与价格动量共振。 |
| 36 | 短期波动调整收益因子 | `实战因子365_cleaned/【实战因子365】36.短期波动调整收益因子(IC 0.0461,sharpe 1.8637).md` | `-pn_Rank(ts_Sum(dt["close"] - dt["open"], 15)) * pn_Rank(ts_Stdev(dt["close"], 15))` | `open`, `close` | **ready** | 待测试 | 日内收益强度与收盘价波动率排名相乘后取负。 |
| 37 | 成交量稳定收盘价因子 | `实战因子365_cleaned/【实战因子365】37.成交量稳定收盘价因子(IC 0.0556,sharpe 1.7222).md` | `pn_Rank(dt["vol"]) * (1 - pn_Rank(ts_Stdev(dt["close"], 10)))` | `vol`, `close` | **ready** | 待测试 | 偏好成交活跃且价格波动较低的股票。 |
| 38 | 波动率差异因子 | `实战因子365_cleaned/【实战因子365】38.波动率差异因子(IC 0.0494,sharpe 1.9308).md` | `ts_Percentage(ts_Stdev(dt["vol"], 60), 5) - ts_Percentage(ts_Stdev(pn_CrossResidual(dt["close"], dt["vol"]), 20), 5)` | `vol`, `close` | **proxy** | AR: -1.7%, SR: -0.29, ICIR: -0.31 ⚠️ | 原文需要 `FACTOR_VOL60D` / `FACTOR_TVSD20D`，本地用成交量波动率与量价残差波动率代理，初测效果较差。 |
| 39 | 反向量价排序乘积因子 | `实战因子365_cleaned/【实战因子365】39.反向量价排序乘积因子(IC 0.0468,sharpe 1.7758).md` | `-pn_Rank(dt["close"]) * pn_Rank(dt["vol"])` | `close`, `vol` | **ready** | 待测试 | 收盘价排名与成交量排名相乘后取负，偏向低价格、低成交关注度股票。 |
| 40 | 资金流最大回撤因子 | `实战因子365_cleaned/【实战因子365】40.资金流最大回撤因子(IC 0.0472,sharpe 1.7265).md` | `-ts_MaxDrawdownAbs(dt["net_mf_amount"], 15)` | `net_mf_amount` | **proxy** | 待测试 | 原文 `NET_MF_AMOUNT_V2` 用 `net_mf_amount` 代理。资金流可能为负，使用更稳健的绝对缩放回撤版本。 |
| 41 | 高开动量衰减因子 | `实战因子365_cleaned/【实战因子365】41.高开动量衰减因子(IC 0.0552,sharpe1.4466).md` | `-ts_WMA(dt["high"] - dt["open"], 5)` | `high`, `open` | **ready** | **AR: 12.0%, SR: 0.76, ICIR: 0.64** | 使用加权移动平均，权重线性递增：1,2,3,4,5。捕捉高开高走后可能的短期反转。 |
| 42 | 调整价格反转因子 | `实战因子365_cleaned/【实战因子365】42.调整价格反转因子(IC 0.0391,sharpe 1.4125).md` | `-(safe_div(dt["adj_close"], ts_Delay(dt["adj_close"], 30)) - 1)` | `adj_close` | **ready** | **AR: 15.5%, SR: 0.96, ICIR: 1.01** | 原文 `AF_CLOSE` 映射为本地前复权收盘价 `adj_close`。 |
| 43 | 换手率相对强度反转因子 | `实战因子365_cleaned/【实战因子365】43.换手率相对强度反转因子(IC 0.0363,sharpe 1.4484).md` | `-safe_div(ts_Mean(safe_div(dt["vol"] * 100, dt["float_share"]), 20), ts_Mean(safe_div(dt["vol"] * 100, dt["float_share"]), 120))` | `vol`, `float_share` | **proxy** | 待测试 | 原文使用短期换手率均值 / 长期换手率均值，本地构造换手率代理。 |
| 44 | 成交量背离复合动量因子 | `实战因子365_cleaned/【实战因子365】44.成交量背离复合动量因子(IC 0.0432,sharpe 1.4783).md` | `-pn_Rank(ts_Corr(pn_Rank(ts_Mean(dt["close"], 15)), pn_Rank(ts_Mean(dt["vol"], 15)), 10)) * pn_Rank(ts_Mean(dt["totalRet"], 15)) * pn_Rank(ts_Mean(safe_div(dt["vol"] * 100, dt["float_share"]), 15)) * pn_Rank(ts_Mean(dt["vol"], 15))` | `close`, `vol`, `totalRet`, `float_share` | **proxy** | 待测试 | 原文使用收益率、换手率和成交量多维复合；换手率使用本地字段代理。 |
| 48 | 换手率调整的异常价格动量因子 | `实战因子365_cleaned/【实战因子365】48.换手率调整的异常价格动量因子(IC 0.0356,sharpe 1.4895).md` | `-pn_Rank(Log(1 + Abs(pn_CrossResidual(dt["adj_close"], -safe_div(1, safe_div(dt["vol"] * 100, dt["float_share"]))))))` | `adj_close`, `vol`, `float_share` | **proxy** | 待测试 | 原文用换手率倒数解释复权价并取残差，本地用构造换手率代理。 |
| 49 | 波动趋势复合因子 | `实战因子365_cleaned/【实战因子365】49.波动趋势复合因子(IC 0.0434,sharpe 1.4998).md` | `Round(safe_div(ts_EMA(dt["close"], 10), ts_Mean(dt["close"], 5))) * (ts_Stdev(dt["totalRet"], 120) - ts_Stdev(dt["totalRet"], 20)) + (ts_IR(dt["totalRet"], 120) - ts_IR(dt["totalRet"], 20))` | `close`, `totalRet` | **proxy** | 待测试 | 原文使用 EMA/MA、长短期波动率和长短期 Sharpe 差，本地用价格和收益率代理。 |
| 50 | 反向标准化后的最大衰减量价复合因子 | `实战因子365_cleaned/【实战因子365】50.反向标准化后的最大衰减量价复合因子(IC 0.0419,sharpe 1.4883).md` | `-pn_Stand(ts_Max(ts_Decay(dt["totalRet"], 20) * Log(dt["vol"] + 1), 3))` | `totalRet`, `vol` | **proxy** | 待测试 | 原文使用 `CHANGE_PCT` 与 `LOG(VOLUME+1)`，本地用 `totalRet` 和 `vol` 代理。 |
| 52 | 大单流出动量反转因子 | `实战因子365_cleaned/【实战因子365】52.大单流出动量反转因子(IC 0.0588,sharpe 1.4998).md` | `-(safe_div(dt["vol"] * 100, dt["float_share"]) + ts_Delta(ts_Delta(dt["sell_lg_vol"], 30), 30))` | `vol`, `float_share`, `sell_lg_vol` | **proxy** | 待测试 | 原文使用大单流出二阶动量，本地用 `sell_lg_vol` 的二阶差分近似。 |
| 56 | 现金流价量趋势因子 | `实战因子365_cleaned/【实战因子365】56.现金流价量趋势因子(IC 0.0344,sharpe 1.4981).md` | `pn_Rank(safe_div(dt["c_fr_sale_sg"], dt["total_mv"])) - pn_Rank(ts_Stdev(dt["adj_close"], 60))` | `c_fr_sale_sg`, `total_mv`, `adj_close` | **proxy** | **AR: 9.6%, SR: 0.71, ICIR: 0.61** | 简化代理版本。使用课程资料中的 `c_fr_sale_sg` 和 `total_mv` 计算现金流/市值，并减去复权价60日波动排名。 |

---

## 2026-05-21 补充覆盖

本节补充本次全量实现任务中新增实现或归类的源因子。完整测试结果与 metrics 路径见 `group_work/FACTOR_IMPLEMENTATION_PROGRESS.md`。

| Factor ID | Factor Name | Formula | Required Fields | Status | Notes |
|---|---|---|---|---|---|
| 11 | 波动换手耦合因子 | `-pn_Stand(pn_Rank(ts_Stdev(dt["close"], 15))) * dt["turnover_rate"]` | `close`, `turnover_rate` | **ready** | 原文 `SCALE(RANK(TS_STDDEV(CLOSE,15))) * -1 * TURN_RATE`，本地有 `turnover_rate`。 |
| 18 | 量价衰减协同因子 | `-ts_Percentage(pn_Rank(dt["close"]), 10) * ts_Decay(ts_ChgRate(dt["vol"], 12), 60)` | `close`, `vol` | **ready** | `FACTOR_VROC12D` 按源含义由12日成交量变化率派生。 |
| 20 | 资金流入线性衰减因子 | `ts_Decay(ts_Sum(dt["net_mf_amount"], 20), 10)` | `net_mf_amount` | **proxy** | `MAIN_IN_FLOW_20D_V2` 用本地20日主力净流入金额代理。 |
| 21 | 资金流入动量因子 | blocked | `REINSTATEMENT_CHG_60D`, `MAIN_IN_FLOW_20D_V2` | **no** | `REINSTATEMENT_CHG_60D` 本地无可信等价字段；不强行用价格涨跌替代。 |
| 23 | 主力流入动量因子 | `ts_Percentage(ts_Decay(ts_Sum(dt["net_mf_amount"], 20), 6), 3)` | `net_mf_amount` | **proxy** | 主力20日流入用 `net_mf_amount` rolling sum 代理。 |
| 24 | 资金流入线性衰减因子 | `ts_Decay(pn_Rank(ts_Sum(dt["net_mf_amount"], 20) - (dt["buy_elg_amount"] - dt["sell_elg_amount"])), 15)` | `net_mf_amount`, `buy_elg_amount`, `sell_elg_amount` | **proxy** | `SLARGE_IN_FLOW_V2` 用超大单净买入金额代理。 |
| 25 | 资金流入动量波动因子 | `ts_Percentage(ts_Sum(dt["net_mf_amount"], 20), 10) * ts_Stdev(dt["totalRet"], 60)` | `net_mf_amount`, `totalRet` | **proxy** | `FACTOR_VOL60D` 在该资金流波动场景用60日收益波动率代理。 |
| 27 | 主力与大单流入差值线性衰减因子 | `ts_Decay(ts_Sum(dt["net_mf_amount"], 20), 5) - ts_Decay(dt["buy_elg_amount"] - dt["sell_elg_amount"], 5)` | `net_mf_amount`, `buy_elg_amount`, `sell_elg_amount` | **proxy** | 主力和超大单资金流均用本地资金流矩阵代理。 |
| 29 | 资金流入动量波动率因子 | `ts_Decay(ts_Sum(dt["net_mf_amount"], 20), 10) * ts_Stdev(dt["totalRet"], 60)` | `net_mf_amount`, `totalRet` | **proxy** | 资金流衰减项可实现，波动率项用60日收益波动代理。 |
| 30 | 动量资金流因子 | `ts_Decay(ts_Stdev(dt["totalRet"], 60), 10) * ts_Percentage(ts_Sum(dt["net_mf_amount"], 20), 10)` | `totalRet`, `net_mf_amount` | **proxy** | 复现 `FACTOR_VOL60D` 与主力20日流入强度的乘法结构。 |
| 32 | 综合动量流动因子 | `ts_Decay(ts_ChgRate(dt["vol"], 12), 10) + ts_Decay(ts_Sum(dt["net_mf_amount"], 20), 10)` | `vol`, `net_mf_amount` | **proxy** | `FACTOR_VROC12D` 可派生，主力流入项用本地资金流代理。 |
| 33 | 复权价波动率比因子 | `safe_div(ts_Stdev(ts_ChgRate(dt["adj_close"], 60), 35), ts_Stdev(ts_Stdev(pn_CrossResidual(dt["close"], dt["vol"]), 20), 35))` | `adj_close`, `close`, `vol` | **proxy** | `REINSTATEMENT_CHG_60D` 用60日复权价变化率代理，`FACTOR_TVSD20D` 用量价残差波动率代理。 |
| 34 | 逆向波动率协方差因子 | `-ts_Cov(ts_ChgRate(dt["vol"], 12), ts_Stdev(pn_Rank(dt["close"]), 15), 20)` | `vol`, `close` | **ready** | `FACTOR_VROC12D` 按12日成交量变化率派生，其他字段可直接映射。 |
| 45 | 对数动量逆向排序因子 | `-pn_Rank(pn_Stand(Log(1 + ts_ChgRate(dt["close"], 15) + ts_ChgRate(dt["adj_close"], 252))))` | `close`, `adj_close` | **proxy** | `FACTOR_ROCTTM` 本地无同名字段，用252日复权价变化率代理。 |
| 46 | 复合价格动能衰减与反转预期因子 | `-(ts_Rank(dt["close"], 20) * ((ts_TopKSum(dt["high"], 20, 5) - ts_Median(dt["close"], 20)) + ts_AvDiff(dt["close"], 20)))` | `close`, `high` | **ready** | 新增 `ts_TopKSum` 与 `ts_AvDiff` 支持原文 `TS_MAX_SUM` / `TS_AV_DIFF`。 |
| 47 | 非线性量价极端反转因子 | `-((ts_Corr(dt["close"], dt["vol"], 30) + ts_Corr(dt["close"], dt["vol"] * dt["vol"], 30) + ts_Max(ts_Kurtosis(dt["totalRet"], 20), 3)) * SignedSqrt(dt["vol"]))` | `close`, `vol`, `totalRet` | **proxy** | 原文 `TS_POLY_REGRESSION` 输出语义不清，采用一阶/二阶量价滚动相关作为非线性关系代理。 |
| 51 | 量价资金非线性因子 | `-(Sin(ts_Mean(dt["adj_close"] / ts_Delay(dt["adj_close"], 1) - 1, 5)) * pn_CSSkew(dt["vwap"]) * ts_Median(ts_Sum(dt["net_mf_amount"], 10), 20) + Log(1 + ts_MaxStd(dt["adj_high"] - dt["adj_low"], 60, 3)) * safe_div(ts_MaxMean(dt["vol"], 20, 5), ts_Mean(dt["vol"], 20)))` | `adj_close`, `vwap`, `net_mf_amount`, `adj_high`, `adj_low`, `vol` | **proxy** | `vwap` 由 `amount / vol` 计算，资金项用本地主力净流入代理。 |
| 53 | 量价资金流截面分位数因子 | `-pn_Rank(Round(ts_MinDiff(dt["vwap"] + ts_MinDiff(dt["adj_high"], 10), 15) * pn_CSPct(ts_Sum(dt["net_mf_amount"], 20) + ts_Sum((dt["buy_lg_amount"] - dt["sell_lg_amount"]) + (dt["buy_elg_amount"] - dt["sell_elg_amount"]), 10), 0.8)))` | `vwap`, `adj_high`, `net_mf_amount`, `buy_lg_amount`, `sell_lg_amount`, `buy_elg_amount`, `sell_elg_amount` | **proxy** | 机构资金项由大单和超大单净买入金额代理。 |
| 54 | 反向行业主力资金排序盈利质量调整因子 | `-pn_Rank(pn_GroupRank(ts_Sum(dt["net_mf_amount"], 20), dt["hy"]) - pn_CSPct(safe_div(dt["NetProfitTTMQ1"], dt["NetAssetQ1"]) - ts_Min(ts_Delta(safe_div(dt["NetProfitTTMQ1"], dt["TotalAssetQ1"]), 250), 250), 0.5))` | `net_mf_amount`, `hy`, `NetProfitTTMQ1`, `NetAssetQ1`, `TotalAssetQ1` | **proxy** | 5年ROE/ROA变化字段缺失，用本地TTM/Q1盈利能力矩阵做代理。 |
| 55 | 行业中性均线价差估值因子 | `-pn_Rank(pn_GroupStdev(((ts_Mean(dt["close"], 3) + ts_Mean(dt["close"], 6) + ts_Mean(dt["close"], 12) + ts_Mean(dt["close"], 24)) / 4) - ts_EMA(dt["close"], 60), dt["hy"]) * Winsorize(safe_div(dt["close"], ts_Mean(dt["close"], 60)) - 1, 1) + safe_div(dt["total_mv"], dt["ebitda"]))` | `close`, `hy`, `total_mv`, `ebitda` | **proxy** | 源文件标题写“大单流出动量反转”，正文实际是行业中性均线价差估值因子；按正文公式实现。 |

---

## 2026-05-23 新增筛选因子

本节记录从 `main` 分支 `group_work/factor_add/` 实验目录筛出的增强因子，并将其补入正式 `FACTOR_REGISTRY`。

| Registry Key | Factor Name | Formula | Required Fields | Status | Notes |
|---|---|---|---|---|---|
| `factor_add_06_quality_x_flow` | 盈利质量 × 主力资金流因子 | `pn_Rank(safe_div(dt["NetProfitTTMQ1"], dt["NetAssetQ1"])) * pn_Rank(ts_Sum(dt["net_mf_amount"], 20))` | `NetProfitTTMQ1`, `NetAssetQ1`, `net_mf_amount` | **screened_addon** | 来自 `factor_add_06_quality_x_flow` 候选实验；保留原 registry key 以便追溯实验结果。 |

---

## 2026-05-23 行业中性增强过线因子

本节记录从 `main` 分支 `group_work/factor_add_new/` 补齐的 3 个新增过线因子。它们已沉淀到正式 `FACTOR_REGISTRY`，统一走 `evaluate_factor.py --factor <key>` 口径。

| Registry Key | Base Logic | Formula | Required Fields | Status | Evaluation Results |
|---|---|---|---|---|---|
| `factor_add2_adj_05_f34_15_25_industry` | f34 行业中性增强 | `pn_GroupRank(factor_34_reverse_vroc_rank_vol_cov(rank_vol_window=15, cov_window=25), dt["hy"])` | `close`, `vol`, `hy` | **screened_addon** | AR: 11.56%, SR: 2.03 |
| `factor_add2_adj_07_f18_decay30_industry` | f18 行业中性增强 | `pn_GroupRank(factor_18_price_volume_decay_synergy(rank_window=10, vroc_window=12, decay_window=30), dt["hy"])` | `close`, `vol`, `hy` | **screened_addon** | AR: 15.28%, SR: 2.01 |
| `factor_add2_adj_04_f34_10_30_industry` | f34 行业中性增强 | `pn_GroupRank(factor_34_reverse_vroc_rank_vol_cov(rank_vol_window=10, cov_window=30), dt["hy"])` | `close`, `vol`, `hy` | **screened_addon** | AR: 11.87%, SR: 2.01 |

---

## 2026-05-24 低相关补充过线因子

本节记录为满足“两两 `|corr| < 0.3` 可选出至少 10 个因子”目标新增的 6 个过线因子。它们覆盖缺口、非流动性、隔夜收益、日内上下行波动差、换手加权收益和慢衰减量价协同，已沉淀到正式 `FACTOR_REGISTRY`。

| Registry Key | Base Logic | Formula | Required Fields | Status | Evaluation Results |
|---|---|---|---|---|---|
| `factor_add3_gap_down_3` | 向下跳空缺口 | `ts_Sum(safe_div(dt["high"] - ts_Delay(dt["low"], 1), ts_Delay(dt["low"], 1)).where(dt["high"] < ts_Delay(dt["low"], 1), 0), 3)` | `high`, `low` | **screened_addon** | AR: 49.71%, SR: 3.25 |
| `factor_add3_overnight_reversal_3_industry_inv` | 隔夜收益行业内方向调整 | `-pn_GroupRank(-ts_Mean(dt["overnightRet"], 3), dt["hy"])` | `overnightRet`, `hy` | **screened_addon** | AR: 15.15%, SR: 2.64 |
| `factor_add3_intraday_hml_vol_120_industry_inv` | 日内上/下振幅波动差行业内方向调整 | `-pn_GroupRank(ts_Stdev(dt["adj_high"] / ts_Delay(dt["adj_close"], 1) - 1, 120) - ts_Stdev(dt["adj_low"] / ts_Delay(dt["adj_close"], 1) - 1, 120), dt["hy"])` | `adj_high`, `adj_low`, `adj_close`, `hy` | **screened_addon** | AR: 18.57%, SR: 2.61 |
| `factor_add3_amihud_illiq_10_industry` | Amihud 非流动性行业内排名 | `pn_GroupRank(ts_Mean(Abs(dt["totalRet"]) / dt["amount"], 10), dt["hy"])` | `totalRet`, `amount`, `hy` | **screened_addon** | AR: 22.21%, SR: 2.11 |
| `factor_add3_turnover_weighted_reversal_20_industry` | 换手加权收益反转行业内排名 | `-pn_GroupRank(ts_Sum(dt["totalRet"] * turnover_rate, 20) / ts_Sum(turnover_rate, 20), dt["hy"])` | `totalRet`, `turnover_rate`, `hy` | **screened_addon** | AR: 20.17%, SR: 2.12 |
| `factor_add3_f18_decay90_industry` | f18 慢衰减行业中性增强 | `pn_GroupRank(factor_18_price_volume_decay_synergy(rank_window=10, vroc_window=12, decay_window=90), dt["hy"])` | `close`, `vol`, `hy` | **screened_addon** | AR: 15.96%, SR: 2.09 |

---

## 2026-05-23 参数优化达标因子

本节记录为第二阶段 `AR > 10%`、`SR > 2` 目标沉淀到正式 `FACTOR_REGISTRY` 的参数优化版因子。它们都是已有源因子的可复现窗口/方向变体，不改变正式评估口径；完整 metrics、收益序列、图表和复现命令见根目录 `FACTOR_IMPLEMENTATION_PROGRESS.md`。

| Registry Key | Base Factor | Optimized Construction | Status | Evaluation Results | Notes |
|---|---|---|---|---|---|
| `factor_opt_01_residual_volatility_w5` | `factor_01_residual_volatility` | `window=5` | **screened_param** | AR: 32.67%, SR: 2.881, ICIR: 2.899 | 残差波动率短窗口版，提升收益稳定性。 |
| `factor_opt_01_residual_volatility_w10` | `factor_01_residual_volatility` | `window=10` | **screened_param** | AR: 30.15%, SR: 2.536, ICIR: 2.500 | 残差波动率中短窗口版。 |
| `factor_opt_05_volume_price_divergence_cov_1_20` | `factor_05_volume_price_divergence_cov` | `delta_window=1, cov_window=20` | **screened_param** | AR: 26.64%, SR: 2.104, ICIR: 2.057 | 将协方差窗口从30日缩短到20日。 |
| `factor_opt_07_price_volume_deviation_vol_w15` | `factor_07_price_volume_deviation_vol` | `window=15` | **screened_param** | AR: 33.25%, SR: 2.128, ICIR: 2.046 | 价量偏离波动率15日窗口版。 |
| `factor_opt_13_main_fund_stability_w5` | `factor_13_main_fund_stability` | `window=5` | **screened_param** | AR: 29.08%, SR: 2.001, ICIR: 1.961 | 主力资金稳定性短窗口版，SR 刚超过阈值。 |
| `factor_opt_33_reinstatement_residual_vol_ratio_40_20` | `factor_33_reinstatement_residual_vol_ratio` | `reinstatement_window=40, stdev_window=20` | **screened_param** | AR: 17.13%, SR: 2.553, ICIR: 3.018 | 复权价变化率与量价残差波动比的40/20窗口版。 |
| `factor_opt_33_reinstatement_residual_vol_ratio_80_20` | `factor_33_reinstatement_residual_vol_ratio` | `reinstatement_window=80, stdev_window=20` | **screened_param** | AR: 16.53%, SR: 2.614, ICIR: 3.038 | 同一结构的80/20窗口版，SR 表现更高。 |
| `factor_opt_34_reverse_vroc_rank_vol_cov_5_20` | `factor_34_reverse_vroc_rank_vol_cov` | `rank_vol_window=5, cov_window=20` | **screened_param** | AR: 16.82%, SR: 2.345, ICIR: 2.312 | 成交量变化率与价格排名波动协方差短窗口版。 |
| `factor_opt_47_nonlinear_volume_price_extreme_reversal_30_30_5` | `factor_47_nonlinear_volume_price_extreme_reversal` | `poly_window=30, kurt_window=30, kurt_top_window=5` | **screened_param** | AR: 19.04%, SR: 2.132, ICIR: 2.333 | 非线性量价关系与收益峰度项的参数优化版。 |
| `factor_opt_54_industry_fund_quality_reverse_inv` | `factor_54_industry_fund_quality_reverse` | `-factor_54_industry_fund_quality_reverse()` | **screened_param** | AR: 10.75%, SR: 2.085, ICIR: 2.029 | 原方向收益为负，注册反向版本便于直接复现正向多空收益。 |

---

## 第一阶段小结

本阶段已完成 56 个源因子的公式整理或阻塞归类，其中：

- **ready 因子**：字段基本完全匹配，可优先进入第二阶段批量计算；
- **proxy 因子**：原文字段本地不存在，但可通过本地字段近似复现；
- **no 因子**：暂不进入主筛选，主要原因是数据覆盖率不足、字段对齐问题或当前本地数据无可信替代字段。

建议第二阶段优先测试 `ready` 因子，再从 `proxy` 因子中筛选有效性较高、相关性较低的候选因子。
