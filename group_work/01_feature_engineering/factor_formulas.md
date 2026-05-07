# Factor Formula List

| Factor ID | Factor Name | Source | Formula | Required Fields | Status | Evaluation Results | Notes |
|---|---|---|---|---|---|---|---|
| 05 | 量价背离协动因子 | `实战因子365_cleaned/【实战因子365】05.量价背离协动因子(IC 0.0511,sharpe 1.6598).md` | `-ts_Cov(ts_Delta(dt["vol"], 1), ts_Delta(dt["close"], 1), 30)` | `vol`, `close` | **tested** | **AR: 25.2%, SR: 1.92, ICIR: 1.82** ⭐ | 原文 `VOLUME` 映射为本地成交量 `vol`。 |
| 06 | 均线过滤反转因子 | `实战因子365_cleaned/【实战因子365】06.均线过滤反转因子(IC 0.0273,sharpe 1.8766).md` | `-(ts_Delta(dt["close"], 10)).where(dt["close"] > ts_Sum(dt["close"], 35)/35, 0)` | `close` | **tested** | **AR: 18.2%, SR: 1.45, ICIR: 1.25** | 当收盘价>35日均线时返回负10日价格变化，否则返回0。捕捉均线突破后的反转。 |
| 08 | 流动性稳定度因子 | `实战因子365_cleaned/【实战因子365】08.流动性稳定度因子(IC 0.0500,sharpe 1.9711).md` | `-ts_Mean(pn_Rank(dt["amount"]), 10)` | `amount` | **tested** | **AR: 21.7%, SR: 1.24, ICIR: 1.06** | `RANK` 使用每日截面百分位排名。 |
| 13 | 主力资金稳定性因子 | `实战因子365_cleaned/【实战因子365】13.主力资金稳定性因子(IC 0.0525,sharpe 1.9096).md` | `-ts_Stdev(net_mf_amount, 10)` | `net_mf_amount` | **tested** | **AR: 29.7%, SR: 1.97, ICIR: 1.92** ⭐ | 使用课程资料中的 `net_mf_amount.pkl`（主力净流入金额）替代 `MAIN_IN_FLOW_V2`。 |
| 26 | 双风格IR利差因子 | `实战因子365_cleaned/【实战因子365】26.双风格IR利差因子(IC 0.0369,sharpe 1.9701).md` | `ts_IR(Beta, 20) - ts_IR(Size, 20)` | `Beta`, `Size` | **tested** | AR: 0.2%, SR: 0.04, ICIR: -0.04 ⚠️ | Barra数据日期范围与股票数据不完全对齐，最新日期覆盖率为0%。 |
| 35 | 价差动量因子 | `实战因子365_cleaned/【实战因子365】35.价差动量因子(IC 0.0347,sharpe 1.9148).md` | `(ts_Mean(dt["open"], 10) - ts_Mean(dt["close"], 10)) * pn_Rank(ts_Delta(dt["close"], 10))` | `open`, `close` | **tested** | **AR: 15.4%, SR: 1.28, ICIR: 1.31** | 原文 `RANK` 映射为 `pn_Rank`。 |
| 38 | 波动率差异因子 | `实战因子365_cleaned/【实战因子365】38.波动率差异因子(IC 0.0494,sharpe 1.9308).md` | `ts_Percentage(ts_Stdev(dt["vol"], 60), 5) - ts_Percentage(ts_Stdev(pn_CrossResidual(dt["close"], dt["vol"]), 20), 5)` | `vol`, `close` | **tested** | AR: -1.7%, SR: -0.29, ICIR: -0.31 ⚠️ | 代理版本效果不佳，本地没有原始 `FACTOR_VOL60D` / `FACTOR_TVSD20D` 字段。 |
| 41 | 高开动量衰减因子 | `实战因子365_cleaned/【实战因子365】41.高开动量衰减因子(IC 0.0552,sharpe1.4466).md` | `-ts_WMA(dt["high"] - dt["open"], 5)` | `high`, `open` | **tested** | **AR: 12.0%, SR: 0.76, ICIR: 0.64** | 使用加权移动平均（权重线性递增：1,2,3,4,5）。捕捉高开低走的反转信号。 |
| 42 | 调整价格反转因子 | `实战因子365_cleaned/【实战因子365】42.调整价格反转因子(IC 0.0391,sharpe 1.4125).md` | `-(dt["adj_close"] / ts_Delay(dt["adj_close"], 30) - 1)` | `adj_close` | **tested** | **AR: 15.5%, SR: 0.96, ICIR: 1.01** | 原文 `AF_CLOSE` 映射为本地前复权收盘价 `adj_close`。 |
| 56 | 现金流价量趋势因子 | `实战因子365_cleaned/【实战因子365】56.现金流价量趋势因子(IC 0.0344,sharpe 1.4981).md` | `pn_Rank(c_fr_sale_sg/total_mv) - pn_Rank(ts_Stdev(adj_close, 60))` | `c_fr_sale_sg`, `total_mv`, `adj_close` | **tested** | **AR: 9.6%, SR: 0.71, ICIR: 0.61** | 简化代理版本。使用课程资料中的 `c_fr_sale_sg`(销售现金流)和 `total_mv` 计算。 |
