# 项目代理指南

本文件是未来在本仓库中工作的代理的精简入口。在扫描整个项目之前先阅读此文件。目的是避免在用户只需要小组作业第一阶段和第二阶段工作时加载许多大型或无关的文件。

## 范围

实际的作业工作在 `group_work/` 下。

对于第一阶段和第二阶段，重点关注：

- 因子公式翻译和字段映射；
- 公式所需的可复用算子；
- 已实现的因子函数；
- 单因子评估输出；
- 第二阶段筛选结果。

大多数原始数据导入脚本、课程参考脚本、调试脚本、PDF 和生成的数据文件可以忽略，除非用户明确询问数据准备或底层 bug。

## 推荐阅读顺序

1. `group_work/README.md`
   - 小组作业文件夹的简要概述。

2. `group_work/01_feature_engineering/factor_formulas.md`
   - 主要的第一阶段交付物。
   - 列出候选因子、公式、源 markdown、所需字段、`ready` / `proxy` 状态以及部分测试结果。

3. `group_work/01_feature_engineering/custom_operators.py`
   - 第一阶段新增算子。
   - 这些应对应复制到 `code/stock1800/feature.py` 中的算子。

4. `code/stock1800/feature.py`
   - 运行时算子库。
   - 评估代码从此处导入算子，而非直接从 `custom_operators.py` 导入。
   - 重要函数包括 `pn_TransNorm`、`get_ls_post`、`pn_Rank`、`pn_CrossResidual`、`ts_Cov`、`ts_Percentage`、`ts_IR`、`ts_WMA`、`ts_EMA` 和其他时间序列/截面算子。

5. `group_work/factor_lib/factors.py`
   - 主要因子实现文件。
   - 每个 `factor_xx_*` 函数实现一个翻译后的因子。
   - `FACTOR_REGISTRY` 决定哪些因子可以被评估脚本调用。

6. `group_work/factor_lib/data_loader.py`
   - 数据加载和掩码工具。
   - 仅在调试数据根路径、pickle 兼容性、股票池掩码或上市日过滤器时阅读。

7. `group_work/02_factor_calculation/evaluate_factor.py`
   - 单因子评估脚本。
   - 计算多空收益、多头超额收益、空头超额收益、IC、年化收益、夏普比率、IC 均值和 ICIR。
   - 将指标 CSV、日收益 CSV 和累计收益 PNG 写入 `group_work/02_factor_calculation/outputs/`。

8. `group_work/02_factor_calculation/outputs/`
   - 第二阶段单因子输出产物。
   - 使用 `*_metrics.csv` 查看数值表现，`*_daily_returns.csv` 查看收益序列，`*_cumret.png` 查看图表。

9. `group_work/03_factor_screening/factor_results.md`
   - 第二阶段筛选总结/报告。
   - 解释已选因子和筛选规则的良好起点。

10. `group_work/03_factor_screening/stage2_outputs/`
    - 批量筛选输出：全因子指标、收益、相关性和变体搜索 CSV。

11. `group_work/03_factor_screening/stage2_next_steps.md`
    - 筛选后的后续备注和可能的改进。

## 主要文件和角色

### 第一阶段：特征工程

| 文件 | 角色 |
|---|---|
| `group_work/01_feature_engineering/factor_formulas.md` | 主要的第一阶段交付物。描述翻译后的因子公式、数据字段、源文件、状态和备注。 |
| `group_work/01_feature_engineering/custom_operators.py` | 第一阶段自定义算子。用于记录添加了哪些算子。 |
| `code/stock1800/feature.py` | 实际的共享运行时算子库。如果评估因缺少算子而失败，请在此处检查。 |
| `实战因子365_cleaned/` | 因子逻辑的源 markdown。仅在需要来源或原始措辞时打开特定因子文件。 |

### 第二阶段：因子计算

| 文件 | 角色 |
|---|---|
| `group_work/factor_lib/factors.py` | 核心因子实现库。用于解释或修改因子逻辑。 |
| `group_work/factor_lib/__init__.py` | 暴露 `FACTOR_REGISTRY`。通常无需阅读。 |
| `group_work/factor_lib/data_loader.py` | 加载本地矩阵字段，处理 pickle 兼容性，解析数据根路径，构建掩码。 |
| `group_work/02_factor_calculation/evaluate_factor.py` | 按名称评估一个因子并保存指标/收益/图表输出。 |
| `group_work/02_factor_calculation/outputs/` | 单个因子的评估产物。用于报告中的证据。 |

### 第二阶段：筛选

| 文件 | 角色 |
|---|---|
| `group_work/03_factor_screening/evaluate_factor.py` | 筛选文件夹中单因子评估器的另一副本/变体。 |
| `group_work/03_factor_screening/factor_results.md` | 人类可读的筛选结果报告。 |
| `group_work/03_factor_screening/stage2_outputs/` | 全因子指标、收益、相关性、选定变体和变体搜索的 CSV 输出。 |
| `group_work/03_factor_screening/stage2_next_steps.md` | 关于严格因子、候选调整、相关性处理和推荐下一步的备注。 |
| `group_work/03_factor_screening/stage2_factor_screening.py` | 预期的批量筛选脚本。当前本地文件在开头附近似乎不完整/截断，因此在依赖它重新运行之前请验证语法。 |

## 常用命令

运行单因子评估：

```powershell
conda run -n bishe python group_work\02_factor_calculation\evaluate_factor.py --factor factor_42_adjusted_price_reversal
```

将因子名称更改为 `FACTOR_REGISTRY` 中的任何 key。

常见示例：

```powershell
conda run -n bishe python group_work\02_factor_calculation\evaluate_factor.py --factor factor_05_volume_price_divergence_cov
conda run -n bishe python group_work\02_factor_calculation\evaluate_factor.py --factor factor_13_main_fund_stability
conda run -n bishe python group_work\02_factor_calculation\evaluate_factor.py --factor factor_56_cashflow_price_trend
```

在重新运行批量筛选之前，检查/修复：

```powershell
group_work\03_factor_screening\stage2_factor_screening.py
```

因为该文件目前顶部看起来被截断了。

## 第一阶段和第二阶段应忽略的内容

除非用户明确询问数据收集、完整课程框架、Barra 建模、遗传编程或调试旧运行，否则忽略以下内容。

根目录级别的草稿脚本和日志已移至 `archive/root_scratch/`。这包括本地诊断以及以前的跟踪调试脚本 `debug_*.py` 和 `evaluate_factors_all.py`；这些脚本现已归档，被 Git 忽略，不再是正式跟踪代码的一部分。

| 路径 / 模式 | 通常跳过的原因 |
|---|---|
| `code/updateData/` | Tushare 原始数据下载脚本。第一阶段/第二阶段报告或因子解释不需要。 |
| `code/combine/` | 原始数据清洗和矩阵生成。仅在重建数据集时有用。 |
| `code/stock1800/v0_getPxData.py` | 原始股票池提取脚本。除非质疑股票池，否则不需要。 |
| `code/stock1800/v1_dataToFactor.py` | 原始课堂风格单因子研究脚本。仅作为参考有用。 |
| `code/stock1800/v2_factorOptComp.py` | 原始 optuna/组合演示。通常超出小组作业第一阶段/第二阶段交付物范围。 |
| `code/stock1800/report_Daily/` | 大型 PDF 参考报告。仅在用户询问研究来源材料时打开。 |
| `code/stock1800/classwork_pdf_text/` | 提取的报告文本。通常不需要。 |
| `data_1800/stock1000/` | 课程参考数据和高级脚本。包括 Barra、组合优化、Smart Beta、GP。对当前任务通常过于宽泛。 |
| `data_1800/stock1000/barra/` | Barra 风格因子和风险模型实现。仅在 Barra/风险模型问题时相关。 |
| `data_1800/stock1000/gp/` | 遗传规划因子挖掘。不是当前第一阶段/第二阶段小组作业的一部分。 |
| `archive/root_scratch/check_*.py`、`debug_*.py`、`test_*.py`、`convert_data.py`、`evaluate_factors_all.py` | 用于数据对齐、掩码、因子 26、pickle 结构和快速批量检查的一次性诊断。 |
| `archive/root_scratch/extract_conversations*.py`、`final_extract.py`、`analyze_jsonl.py` | Codex 对话日志提取辅助工具，不是因子工作流代码。 |
| `archive/root_scratch/rollout-*.jsonl`、`archive/root_scratch/codex对话记录.txt` | 之前的对话产物，不是项目逻辑。 |

## 当前作业逻辑

第一阶段主要是：

- 选择和记录候选因子；
- 将公式翻译为本地字段/算子表示法；
- 将精确实现标记为 `ready`，近似实现标记为 `proxy`；
- 添加或记录任何缺失的算子。

第二阶段主要是：

- 在 `group_work/factor_lib/factors.py` 中实现因子函数；
- 在 `group_work/02_factor_calculation/evaluate_factor.py` 中运行评估器；
- 使用 `group_work/02_factor_calculation/outputs/` 中的输出；
- 使用 `group_work/03_factor_screening/factor_results.md` 和 `stage2_outputs/` 进行总结或筛选。

## 重要注意事项

- `custom_operators.py` 是文档/第一阶段支持。运行时评估从 `code/stock1800/feature.py` 导入算子。
- `factor_38_volatility_difference_proxy` 明确是代理，因为原始字段 `FACTOR_VOL60D` 和 `FACTOR_TVSD20D` 在本地检出中不直接存在。
- 部分因子使用代理字段，如从 `vol` 和 `float_share` 构建的换手率，或如 `net_mf_amount` 的资金流替代。
- `evaluate_factor.py` 是本地验证/评估工具。主要作用是，验证第一阶段的公式和算子能够正常运行。
- 项目有许多生成的数据文件和输出产物。除非为特定问题所需，否则不要加载大型数据或 PDF。

## 未来代理快速决策规则

- 如果被问"这个因子公式/字段"：先读 `factor_formulas.md`。
- 如果被问"这个因子怎么实现"：读 `group_work/factor_lib/factors.py`。
- 如果被问"为什么跑不通/字段缺失/mask 很多"：读 `data_loader.py`，然后读具体因子函数。
- 如果被问"这个因子效果如何"：读 `group_work/02_factor_calculation/outputs/` 中的对应文件。
- 如果被问"二阶段选了哪些因子/筛选规则是什么"：读 `group_work/03_factor_screening/factor_results.md` 和 `stage2_outputs/` 中的相关 CSV。
- 如果被问"项目原始数据如何生成"：读 `code/updateData/`、`code/combine/` 和 `code/stock1800/v0_getPxData.py`；否则跳过。
