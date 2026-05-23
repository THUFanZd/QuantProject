当前 `group_work` 的 Stage 2 主要是因子筛选，不是完整组合回测。请先读 `C:\Users\lzx\Desktop\研一下\量化\Project\group_work\03_factor_screening\stage2_factor_screening.py` 和同目录的 `evaluate_factor.py`，再对照课程资料里的完整脚本。核心差异如下：

| 当前 Stage 2 缺口 | 当前脚本怎么做 | 应该对照读哪个完整脚本 |
|---|---|---|
| 没有真正构建指数增强组合 | 只对每个因子算标准化多空组合收益：`factor_port.shift(2) * totalRet` | `课程资料（中证1000）\stock1000\v5_portfolioExposureOpt.py` |
| 没有基准指数权重约束 | 只用因子多空权重，不围绕 `idxWgt` 做主动权重 | `v5_portfolioExposureOpt.py` |
| 没有 Barra 风格暴露控制 | 只看因子相关性，没有约束 Size、Beta、Momentum 等风格暴露 | `v5_portfolioExposureOpt.py` |
| 没有行业暴露控制 | 没有行业哑变量或行业偏离约束 | `v5_portfolioExposureOpt.py` |
| 没有风险模型 | 不使用风格协方差、特质风险，也不算主动风险 | `v5_portfolioExposureOpt.py`；风险数据来源看 `stock1000\barra\v2_barra_stats.py` |
| 没有组合优化 | 只是按 AR、SR、ICIR、覆盖率、相关性筛因子 | `v5_portfolioExposureOpt.py` |
| 没有换手约束 | 每天因子权重变化，但没有限制换手 | `stock1000\v8_alpha_turnover.py` |
| 没有显式交易成本 | 收益里基本没有扣交易成本 | `stock1000\question2_alpha_cost.py` |
| 没有完整绩效评价 | 主要看单因子 AR、SR、IC、ICIR；缺少相对基准的超额收益、跟踪误差、信息比率、回撤等 | `v5_portfolioExposureOpt.py` |

一句话：`group_work` Stage 2 是“用简化多空回测筛因子”；`v5_portfolioExposureOpt.py` 是“把 alpha 放进 Barra 风险模型和指数增强优化里做组合回测”；`v8_alpha_turnover.py` 补换手约束；`question2_alpha_cost.py` 补交易成本。