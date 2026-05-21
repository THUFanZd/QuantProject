# Project Agent Guide

This file is the compact entry point for future agents working in this repo.
Read this before scanning the whole project. The goal is to avoid loading many
large or irrelevant files when the user only needs the group assignment stage 1
and stage 2 work.

## Scope

The practical assignment work is under `group_work/`.

For stage 1 and stage 2, focus on:

- factor formula translation and field mapping;
- reusable operators needed by the formulas;
- implemented factor functions;
- single-factor evaluation outputs;
- stage-2 screening results.

Most original data-ingestion scripts, course reference scripts, debug scripts,
PDFs, and generated data files can be ignored unless the user explicitly asks
about data preparation or a low-level bug.

## Recommended Reading Order

1. `group_work/README.md`
   - Very short overview of the group-work folder.

2. `group_work/01_feature_engineering/factor_formulas.md`
   - Main stage-1 deliverable.
   - Lists candidate factors, formulas, source markdown, required fields,
     `ready` / `proxy` status, and some test results.

3. `group_work/01_feature_engineering/custom_operators.py`
   - Stage-1 added operators.
   - These should correspond to operators copied into `code/stock1800/feature.py`.

4. `code/stock1800/feature.py`
   - Runtime operator library.
   - Evaluation code imports operators from here, not directly from
     `custom_operators.py`.
   - Important functions include `pn_TransNorm`, `get_ls_post`, `pn_Rank`,
     `pn_CrossResidual`, `ts_Cov`, `ts_Percentage`, `ts_IR`, `ts_WMA`,
     `ts_EMA`, and other time-series/cross-sectional operators.

5. `group_work/factor_lib/factors.py`
   - Main factor implementation file.
   - Each `factor_xx_*` function implements one translated factor.
   - `FACTOR_REGISTRY` determines which factors can be called by evaluation
     scripts.

6. `group_work/factor_lib/data_loader.py`
   - Data-loading and mask utilities.
   - Read this only when debugging data roots, pickle compatibility, universe
     masks, or listing-day filters.

7. `group_work/02_factor_calculation/evaluate_factor.py`
   - Single-factor evaluation script.
   - Computes long-short return, long excess return, short excess return, IC,
     annualized return, Sharpe, IC mean, and ICIR.
   - Writes metrics CSV, daily returns CSV, and cumulative-return PNG into
     `group_work/02_factor_calculation/outputs/`.

8. `group_work/02_factor_calculation/outputs/`
   - Stage-2 single-factor output artifacts.
   - Use `*_metrics.csv` for numeric performance, `*_daily_returns.csv` for
     return series, and `*_cumret.png` for plots.

9. `group_work/03_factor_screening/factor_results.md`
   - Stage-2 screening summary/report.
   - Good starting point for explaining selected factors and screening rules.

10. `group_work/03_factor_screening/stage2_outputs/`
    - Batch screening outputs: all-factor metrics, returns, correlations, and
      variant-search CSVs.

11. `group_work/03_factor_screening/stage2_next_steps.md`
    - Follow-up notes and possible improvements after screening.

## Main Files And Roles

### Stage 1: Feature Engineering

| File | Role |
|---|---|
| `group_work/01_feature_engineering/factor_formulas.md` | Primary stage-1 deliverable. Describes translated factor formulas, data fields, source files, status, and notes. |
| `group_work/01_feature_engineering/custom_operators.py` | Stage-1 custom operators. Useful for documenting what operators were added. |
| `code/stock1800/feature.py` | Actual shared operator library used at runtime. If an evaluation fails because an operator is missing, check here. |
| `实战因子365_cleaned/` | Source markdown for factor logic. Only open specific factor files when provenance or original wording is needed. |

### Stage 2: Factor Calculation

| File | Role |
|---|---|
| `group_work/factor_lib/factors.py` | Core factor implementation library. Use this to explain or modify factor logic. |
| `group_work/factor_lib/__init__.py` | Exposes `FACTOR_REGISTRY`. Usually no need to read. |
| `group_work/factor_lib/data_loader.py` | Loads local matrix fields, handles pickle compatibility, resolves data root, and builds masks. |
| `group_work/02_factor_calculation/evaluate_factor.py` | Evaluates one factor by name and saves metrics/returns/plot outputs. |
| `group_work/02_factor_calculation/outputs/` | Evaluation artifacts for individual factors. Use these for evidence in reports. |

### Stage 2: Screening

| File | Role |
|---|---|
| `group_work/03_factor_screening/evaluate_factor.py` | Another copy/variant of the single-factor evaluator inside the screening folder. |
| `group_work/03_factor_screening/factor_results.md` | Human-readable screening result report. |
| `group_work/03_factor_screening/stage2_outputs/` | CSV outputs for all-factor metrics, returns, correlations, selected variants, and variant search. |
| `group_work/03_factor_screening/stage2_next_steps.md` | Notes on strict factors, candidate adjustments, correlation handling, and recommended next steps. |
| `group_work/03_factor_screening/stage2_factor_screening.py` | Intended batch screening script. Current local file appears incomplete/truncated near the start, so verify syntax before relying on it for reruns. |

## Useful Commands

Run a single-factor evaluation:

```powershell
conda run -n bishe python group_work\02_factor_calculation\evaluate_factor.py --factor factor_42_adjusted_price_reversal
```

Change the factor name to any key in `FACTOR_REGISTRY`.

Common examples:

```powershell
conda run -n bishe python group_work\02_factor_calculation\evaluate_factor.py --factor factor_05_volume_price_divergence_cov
conda run -n bishe python group_work\02_factor_calculation\evaluate_factor.py --factor factor_13_main_fund_stability
conda run -n bishe python group_work\02_factor_calculation\evaluate_factor.py --factor factor_56_cashflow_price_trend
```

Before rerunning batch screening, inspect/fix:

```powershell
group_work\03_factor_screening\stage2_factor_screening.py
```

because the file currently looks truncated at the top.

## What To Ignore For Stage 1 And Stage 2

Ignore these unless the user explicitly asks about data collection, full course
frameworks, Barra modeling, genetic programming, or debugging old runs.

Root-level scratch scripts and logs have been moved to `archive/root_scratch/`.
This includes local diagnostics plus the former tracked debug scripts
`debug_*.py` and `evaluate_factors_all.py`; those scripts are now archived,
ignored by Git, and no longer part of the formal tracked code surface.

| Path / Pattern | Why usually skip |
|---|---|
| `code/updateData/` | Tushare raw data download scripts. Not needed for stage-1/2 report or factor explanation. |
| `code/combine/` | Raw data cleaning and matrix generation. Useful only if rebuilding the dataset. |
| `code/stock1800/v0_getPxData.py` | Original stock-pool extraction script. Not needed unless the stock universe is questioned. |
| `code/stock1800/v1_dataToFactor.py` | Original classroom-style single-factor research script. Useful only as reference. |
| `code/stock1800/v2_factorOptComp.py` | Original optuna/combination demo. Usually outside the group-work stage-1/2 deliverable. |
| `code/stock1800/report_Daily/` | Large PDF reference reports. Open only when the user asks about research source material. |
| `code/stock1800/classwork_pdf_text/` | Extracted report text. Usually not needed. |
| `data_1800/stock1000/` | Course reference data and advanced scripts. Includes Barra, portfolio optimization, Smart Beta, GP. Usually too broad for current task. |
| `data_1800/stock1000/barra/` | Barra style factor and risk model implementation. Only relevant for Barra/risk-model questions. |
| `data_1800/stock1000/gp/` | Genetic programming factor mining. Not part of current stage-1/2 group work. |
| `archive/root_scratch/check_*.py`, `debug_*.py`, `test_*.py`, `convert_data.py`, `evaluate_factors_all.py` | One-off diagnostics for data alignment, masks, factor 26, pickle structure, and quick batch checks. |
| `archive/root_scratch/extract_conversations*.py`, `final_extract.py`, `analyze_jsonl.py` | Codex conversation-log extraction helpers, not factor-workflow code. |
| `archive/root_scratch/rollout-*.jsonl`, `archive/root_scratch/codex对话记录.txt` | Prior conversation artifacts, not project logic. |

## Current Assignment Logic

Stage 1 is mainly:

- choose and document candidate factors;
- translate formulas into local field/operator notation;
- mark exact implementations as `ready` and approximations as `proxy`;
- add or document any missing operators.

Stage 2 is mainly:

- implement factor functions in `group_work/factor_lib/factors.py`;
- run the evaluator in `group_work/02_factor_calculation/evaluate_factor.py`;
- use outputs from `group_work/02_factor_calculation/outputs/`;
- summarize or screen using `group_work/03_factor_screening/factor_results.md`
  and `stage2_outputs/`.

## Important Caveats

- `custom_operators.py` is documentation/stage-1 support. Runtime evaluation
  imports operators from `code/stock1800/feature.py`.
- `factor_38_volatility_difference_proxy` is explicitly a proxy because the
  original fields `FACTOR_VOL60D` and `FACTOR_TVSD20D` are not directly present
  in the local checkout.
- Some factors use proxy fields such as constructed turnover from `vol` and
  `float_share`, or fund-flow substitutes such as `net_mf_amount`.
- `evaluate_factor.py` is a local validation/evaluation utility. It supports
  stage 2 evidence, but for stage 1 the essential deliverables are formulas and
  operators.
- The project has many generated data files and output artifacts. Do not load
  large data or PDFs unless needed for a specific question.

## Quick Decision Rules For Future Agents

- If asked "这个因子公式/字段/是否 proxy": read `factor_formulas.md` first.
- If asked "这个因子怎么实现": read `group_work/factor_lib/factors.py`.
- If asked "为什么跑不通/字段缺失/mask 很多": read `data_loader.py`, then the
  specific factor function.
- If asked "这个因子效果如何": read the matching files in
  `group_work/02_factor_calculation/outputs/`.
- If asked "二阶段选了哪些因子/筛选规则是什么": read
  `group_work/03_factor_screening/factor_results.md` and relevant CSVs in
  `stage2_outputs/`.
- If asked "项目原始数据如何生成": then read `code/updateData/`, `code/combine/`,
  and `code/stock1800/v0_getPxData.py`; otherwise skip them.
