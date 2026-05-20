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

## 第一阶段小结

本阶段已完成 36 个候选因子的公式整理，其中：

- **ready 因子**：字段基本完全匹配，可优先进入第二阶段批量计算；
- **proxy 因子**：原文字段本地不存在，但可通过本地字段近似复现；
- **no 因子**：暂不进入主筛选，主要原因是数据覆盖率不足或字段对齐问题。

建议第二阶段优先测试 `ready` 因子，再从 `proxy` 因子中筛选有效性较高、相关性较低的候选因子。