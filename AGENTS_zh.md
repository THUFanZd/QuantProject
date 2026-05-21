# AGENTS.md

本仓库是一个量化因子课程项目。本次任务要求将仓库根目录因子源文件夹中以 `365_cleaned/` 结尾的所有源因子全部实现，或明确归类为受阻（blocked）。

## 必读上下文入口

在广泛扫描之前，请按顺序阅读以下文件：

1. `PROJECT_AGENT_GUIDE_zh.md`
2. `mission_zh.md`
3. `group_work/README.md`
4. `group_work/01_feature_engineering/factor_formulas.md`
5. `group_work/factor_lib/factors.py`
6. `code/stock1800/feature.py`
7. `group_work/factor_lib/data_loader.py`
8. `group_work/FACTOR_IMPLEMENTATION_PROGRESS.md`

不要一开始就读取整个仓库、数据目录、PDF 或归档的草稿脚本。

## 子代理授权

用户明确授权 Codex 为本次任务创建子代理。

使用内置的 Codex `spawn_agent` 工具创建子代理。在本环境中，即原生的 `functions.spawn_agent` 能力。不要使用 `opencode-subagent` 技能、Opencode 或任何外部子代理工作流来完成本次任务。

推荐分工方式：

- 使用探索型子代理处理窄范围代码库问题，例如"资金流代理有哪些矩阵字段？"或"哪些因子已在 `FACTOR_REGISTRY` 中？"
- 使用工作型子代理处理互不重叠的因子 ID 范围。每个工作代理必须拥有不重叠的因子范围，并须被告知其他代理也可能在编辑代码库，因此不得撤销无关的编辑。
- 主 Codex 负责整合工作代理的结果、解决冲突、运行验证并更新进度文件。

为工作代理分配任务时，需提供：

- 需要实现的因子 ID；
- 可编辑的文件；
- 要求的输出格式；
- 列出已更改文件和测试结果的指令。

## 持续性规则

持续工作，直到 `*365_cleaned/` 源文件夹中的每个因子满足以下之一：

- 已实现并注册；
- 已作为文档化的代理实现；
- 归类为数据缺失但易于解决；
- 归类为数据缺失且无法从当前本地数据解决。

不要仅完成规划就停止。不要在因子仍未分类时停止，除非用户中断、重定向，或真正需要用户输入的阻碍出现。

如果发生上下文压缩或中断，请先更新 `group_work/FACTOR_IMPLEMENTATION_PROGRESS.md`，以便下次会话能从确切当前状态恢复。

## 编辑边界

主要可编辑文件：

- `group_work/factor_lib/factors.py`
- `group_work/factor_lib/__init__.py`（仅在必要时）
- `group_work/01_feature_engineering/factor_formulas.md`
- `group_work/01_feature_engineering/custom_operators.py`
- `code/stock1800/feature.py`
- `group_work/FACTOR_IMPLEMENTATION_PROGRESS.md`

避免编辑：

- `code/updateData/`
- `code/combine/`
- `data_1800/`
- `archive/root_scratch/`
- 生成的输出 CSV/PNG 文件，除非测试运行有意重新生成它们。

`group_work/03_factor_screening/stage2_factor_screening.py` 目前不完整，且不是实现单个因子所必需的。在所有因子实现完成之前，不要花时间修复它，除非用户要求。

## 实现标准

对于每个因子：

- 在仓库根目录 `*365_cleaned/` 文件夹下阅读其源 markdown；
- 将源字段映射到本地 `dt[...]` 字段；
- 在需要时，将缺失的可复用算子同时添加到 `code/stock1800/feature.py` 和 `group_work/01_feature_engineering/custom_operators.py`；
- 在 `group_work/factor_lib/factors.py` 中以 `factor_xx_descriptive_name(dt, ...)` 的形式实现该因子；
- 将其添加到 `FACTOR_REGISTRY`；
- 记录其为精确实现、代理实现还是受阻；
- 在可能的情况下运行单因子评估器。

优先使用精确实现。仅在源字段缺失但存在合理的本地替代时才使用代理实现。使用代理时，须在代码注释或文档字符串以及进度文件中清楚记录替代关系。

不要静默编造不可用的数据。

使用 conda bishe 作为 Python 环境。使用 pip install 安装所需的包。

## 验证命令

对于已实现的因子 key：

```powershell
conda run -n bishe python group_work\02_factor_calculation\evaluate_factor.py --factor <factor_key>
```

如果命令因环境/沙箱问题而失败，请将环境失败与因子代码失败分开记录。除非回溯指向因子实现或字段映射，否则不要将该因子标记为有问题。
