# AGENTS.md

本仓库是一个量化因子的项目。目前处于作业要求中的阶段一和阶段二，只用处理这两个阶段的内容。

## 目标

`量化投资分析2026春-大作业要求.md` 中的：
```
3. 计算因子的多空收益指标，筛选出 **10个达标因子**：
   - 因子收益年化 > 10%（`|ar| > 0.1`）
   - 因子收益夏普 > 2（`|sr| > 2`）
   - 因子间相关系数 < 0.3（两两 `|corr| < 0.3`）
```

目前有 14 个因子满足前两条，其中能找出来 7 个因子满足 3 条要求。你的需要是，补充因子，使得能找出来 10 个因子满足这 3 条要求。

## 必读上下文入口

在广泛扫描之前，请按顺序阅读以下文件：

1. `PROJECT_AGENT_GUIDE_zh.md`
2. `group_work/01_feature_engineering/factor_formulas.md`
3. `group_work/factor_lib/factors.py`
4. `code/stock1800/feature.py`
5. `group_work/factor_lib/data_loader.py`

不要一开始就读取整个仓库、数据目录、PDF 或归档的草稿脚本，避免占据过长上下文窗口。

## 子代理授权

用户明确授权 Codex 为本次任务创建子代理。

使用内置的 Codex `spawn_agent` 工具创建子代理。在本环境中，即原生的 `functions.spawn_agent` 能力。不要使用 `opencode-subagent` 技能、Opencode 或任何外部子代理工作流来完成本次任务。

## 工作流

- 主 Codex agent 作为 orchestrator，负责整合工作代理的结果、解决冲突、运行验证并更新进度文件，确保在长程工作中避免过快消耗上下文窗口。
- 子代理根据目前因子库的状况（在\group_work\01_feature_engineering\factor_formulas.md 和根目录下的 FACTOR_IMPLEMENTATION_PROGRESS.md中记录的因子实现情况），尽量找没尝试过的风格的因子，或者自行构思因子，然后进行实现，目的是争取实现上面提到的目标。
- 如果指标不错，就尝试调整参数或者回测方式，看是否能提高指标；如果指标一般，就放弃，继续下一个因子的寻找。
    - `group_work/02_factor_calculation/try1_param_search.py` 是
一个因子后处理方法。你也可以从网上寻找一些其他的后处理方法，让子代理寻找，然后把这些后处理方法沉淀到group_work/02_factor_calculation/factor_postprocessing.py中。
- 子代理每尝试一个因子，就进行一个简短的总结，沉淀到 \group_work\01_feature_engineering\factor_formulas.md 和根目录下的 FACTOR_IMPLEMENTATION_PROGRESS.md 中。
- 新的因子，可以在 C:\Users\lzx\Desktop\研一下\量化\Project\code\stock1800\report_Daily 中选择合适的因子，也可以上网寻找。具体从哪个信息源寻找，需要你这个主 orchestrator 决定，让子代理执行。如果是网上找到的，要在相关字段记录来源。

为工作代理分配任务时，需提供：

- 需要实现的因子 ID；
- 可编辑的文件；
- 要求的输出格式；
- 列出已更改文件和测试结果的指令。

## 结果记录

把满足要求的因子，对应的运行第二阶段脚本的命令，保存在 FACTOR_IMPLEMENTATION_PROGRESS.md 中。包括因子后处理的命令，以及运行回测的命令，让我运行这些命令，就能看到达标因子的回测结果。

## 持续性规则

持续工作，直到任务完成或者用户打断。

## 编辑边界

主要可编辑文件：

- `group_work/factor_lib/factors.py`
- `group_work/factor_lib/__init__.py`（仅在必要时）
- `group_work/01_feature_engineering/factor_formulas.md`
- `group_work/01_feature_engineering/custom_operators.py`
- `code/stock1800/feature.py`
- `FACTOR_IMPLEMENTATION_PROGRESS.md`

避免编辑：

- `code/updateData/`
- `code/combine/`
- `data_1800/`
- `archive/root_scratch/`
- 生成的输出 CSV/PNG 文件，除非测试运行有意重新生成它们。

`group_work/03_factor_screening/stage2_factor_screening.py` 目前不完整，且不是实现单个因子所必需的。在所有因子实现完成之前，不要花时间修复它，除非用户要求。

## 实现标准

满足`目标`中的要求。

不要静默编造不可用的数据。

使用 conda bishe 作为 Python 环境。使用 pip install 安装所需的包。

## 验证命令

对于已实现的因子 key：

```powershell
conda run -n bishe python group_work\02_factor_calculation\evaluate_factor.py --factor <factor_key>
```

可以尝试不同的回测方式，看是否能提高指标。

如果命令因环境/沙箱问题而失败，请将环境失败与因子代码失败分开记录。除非回溯指向因子实现或字段映射，否则不要将该因子标记为有问题。
