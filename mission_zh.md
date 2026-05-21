# 任务：实现源因子

## 目标

在本地数据允许的范围内，实现仓库根目录源文件夹中以 `365_cleaned/` 结尾的所有因子。完成后，用户应能打开 `group_work/FACTOR_IMPLEMENTATION_PROGRESS.md` 并立即看到：

- 哪些因子已成功实现并测试；
- 哪些因子以代理方式实现；
- 哪些因子因数据缺失但易于添加而受阻；
- 哪些因子因当前本地数据无法支持而受阻。

## 重要起点

先阅读 `AGENTS.md`。它授权通过 `spawn_agent` 使用原生 Codex 子代理，并禁止在本次任务中使用 `opencode-subagent` 技能。

然后阅读 `PROJECT_AGENT_GUIDE.md`。它解释了哪些文件重要，哪些大型/无关文件应跳过。

## 第一阶段：了解项目规则

阅读以下文件，保持笔记简洁：

1. `PROJECT_AGENT_GUIDE.md`
2. `group_work/README.md`
3. `group_work/01_feature_engineering/factor_formulas.md`
4. `group_work/01_feature_engineering/custom_operators.py`
5. `code/stock1800/feature.py`
6. `group_work/factor_lib/factors.py`
7. `group_work/factor_lib/data_loader.py`
8. `group_work/02_factor_calculation/evaluate_factor.py`
9. `group_work/FACTOR_IMPLEMENTATION_PROGRESS.md`

需要掌握的关键规则：

- 因子函数位于 `group_work/factor_lib/factors.py`；
- 运行时算子从 `code/stock1800/feature.py` 导入；
- `custom_operators.py` 记录第一阶段自定义算子，应与新增可复用算子保持同步；
- 因子 key 必须添加到 `FACTOR_REGISTRY`；
- 单因子测试使用 `group_work/02_factor_calculation/evaluate_factor.py`；
- `stage2_factor_screening.py` 不完整，单因子实现不需要。

## 第二阶段：盘点当前覆盖情况

在编辑之前建立当前盘点：

1. 列出仓库根目录 `*365_cleaned/` 文件夹下的所有源文件。
2. 列出 `group_work/factor_lib/factors.py` 中所有现有的 `factor_xx_*` 函数。
3. 列出 `FACTOR_REGISTRY` 中的所有 key。
4. 将源因子 ID 与已实现/已注册的 ID 进行比较。
5. 在实现新因子之前，用盘点结果更新 `group_work/FACTOR_IMPLEMENTATION_PROGRESS.md`。

不要假设 `factor_formulas.md` 中记录的公式已经实现。请验证函数和注册表条目。

## 第三阶段：实现因子

对于每个缺失或不完整的因子：

1. 在仓库根目录 `*365_cleaned/` 文件夹中阅读对应的源 markdown。
2. 提取公式、字段名称和预期经济含义。
3. 检查每个源字段是否在本地存在：
   - 首先在 `data_1800/stock1000/data/matrix/` 中查找；
   - 然后在 `data_1800/stock1000/data/finTTM/` 中查找；
   - 然后在 `data_loader.py` 中加载器支持的字段中查找；
   - 除非需要，否则避免广泛的数据扫描。
4. 选择四种结果之一：
   - `success`：使用本地数据的足够精确的实现；
   - `proxy`：合理的本地替代，有清楚文档说明；
   - `missing_easy`：源字段缺失，但如果用户提供或生成明确的数据文件则易于添加；
   - `missing_unsolved`：源字段缺失，且无法从当前本地数据可信地推断。
5. 如果要实现：
   - 在 `code/stock1800/feature.py` 中添加或复用算子；
   - 在 `group_work/01_feature_engineering/custom_operators.py` 中同步新增的可复用算子；
   - 在 `group_work/factor_lib/factors.py` 中添加因子函数；
   - 将其添加到 `FACTOR_REGISTRY`；
   - 如果公式/状态需要更正，更新 `factor_formulas.md`；
   - 立即更新进度文件。

## 第四阶段：测试已实现的因子

对于每个已实现或代理因子，运行：

```powershell
conda run -n bishe python group_work\02_factor_calculation\evaluate_factor.py --factor <factor_key>
```

在 `group_work/FACTOR_IMPLEMENTATION_PROGRESS.md` 中记录：

- 运行的命令；
- 通过/失败；
- 生成的指标路径（如有）；
- 失败时的回溯摘要；
- 失败是与环境相关还是与因子相关。

如果实现了许多因子，可批量测试，但仍需记录每个因子的状态。

## 第五阶段：在有帮助时使用子代理

用户已授权使用原生 Codex 子代理。建议先由主代理完成盘点，跳过已经实现且已注册的因子，只把未完成或需修正的因子分给工作代理。

推荐分工方式：

- 探索代理：只调查，不实现。负责整理本地 `dt[...]` 字段、`feature.py` 已有算子、`factors.py` 已实现函数、`FACTOR_REGISTRY` 已注册 key，以及明显缺失但可能可代理的字段。
- 工作代理 A：最多 5 个未完成因子。
- 工作代理 B：最多 5 个未完成因子。
- 工作代理 C：最多 5 个未完成因子。
- 后续工作代理：继续按每个代理最多 5 个未完成因子的方式分批创建。

每个工作代理只处理分配到的因子，不重复实现已完成因子。这样可以降低单个子代理的上下文占用，提高实现质量。主代理负责分配任务、整合改动、运行测试、解决冲突，并更新进度文件。

不要使用 `opencode-subagent` 技能。

## 第六阶段：最终交付物

在停止之前，确保以下条件成立：

- 每个因子 ID 01-56 在 `group_work/FACTOR_IMPLEMENTATION_PROGRESS.md` 中都有一行记录；
- 每行都有 `success`、`proxy`、`missing_easy`、`missing_unsolved` 或 `not_tested` 之一的状态；
- 所有已实现的因子都在 `FACTOR_REGISTRY` 中；
- 新算子同时存在于运行时和第一阶段文档位置；
- 测试已运行或测试阻碍已记录；
- 最终回复告诉用户在哪里阅读进度文件。

不要在因子仍未分类时停止，除非用户中断。
