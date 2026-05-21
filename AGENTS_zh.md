# AGENTS.md

本仓库是一个量化因子项目。

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
