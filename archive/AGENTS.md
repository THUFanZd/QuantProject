# AGENTS.md

This repository is a quantitative factor course project. For this mission, the
user wants all source factors in the repo-root factor source folder ending with
`365_cleaned/` implemented or explicitly classified as blocked.

## Required Context Entry Points

Before scanning broadly, read these files in order:

1. `PROJECT_AGENT_GUIDE.md`
2. `mission.md`
3. `group_work/README.md`
4. `group_work/01_feature_engineering/factor_formulas.md`
5. `group_work/factor_lib/factors.py`
6. `code/stock1800/feature.py`
7. `group_work/factor_lib/data_loader.py`
8. `group_work/FACTOR_IMPLEMENTATION_PROGRESS.md`

Do not start by reading the full repo, data directories, PDFs, or archived
scratch scripts.

## Subagent Authorization

The user explicitly authorizes Codex to create subagents for this mission.

Use the built-in Codex `spawn_agent` tool for subagents. In this environment
that is the native `functions.spawn_agent` capability. Do not use the
`opencode-subagent` skill, Opencode, or any external subagent workflow for this
mission.

Recommended delegation:

- Use explorer subagents for narrow codebase questions, such as "which matrix
  fields exist for fund-flow proxies?" or "which factors are already in
  `FACTOR_REGISTRY`?"
- Use worker subagents for disjoint factor ID ranges. Each worker must own a
  non-overlapping factor range and must be told that other agents may also be
  editing the codebase, so they must not revert unrelated edits.
- Main Codex remains responsible for integrating worker results, resolving
  conflicts, running verification, and updating the progress file.

When assigning worker tasks, give each worker:

- factor IDs to implement;
- files it may edit;
- required output format;
- instruction to list changed files and test results.

## Persistence Rule

Keep working until every factor in the `*365_cleaned/` source folder is either:

- implemented and registered;
- implemented as a documented proxy;
- classified as missing data but easy to resolve;
- classified as missing data and not solvable from current local data.

Do not stop after planning only. Do not stop while factors remain untriaged
unless the user interrupts, redirects, or a real blocker requires user input.

If context compaction or interruption happens, update
`group_work/FACTOR_IMPLEMENTATION_PROGRESS.md` first so the next session can
resume from the exact current state.

## Editing Boundaries

Primary editable files:

- `group_work/factor_lib/factors.py`
- `group_work/factor_lib/__init__.py` only if necessary
- `group_work/01_feature_engineering/factor_formulas.md`
- `group_work/01_feature_engineering/custom_operators.py`
- `code/stock1800/feature.py`
- `group_work/FACTOR_IMPLEMENTATION_PROGRESS.md`

Avoid editing:

- `code/updateData/`
- `code/combine/`
- `data_1800/`
- `archive/root_scratch/`
- generated output CSV/PNG files unless a test run intentionally regenerates
  them.

`group_work/03_factor_screening/stage2_factor_screening.py` is currently
incomplete and is not required for implementing individual factors. Do not spend
time fixing it until all factor implementations are done, unless the user asks.

## Implementation Standards

For each factor:

- read its source markdown under the repo-root `*365_cleaned/` folder;
- map source fields to local `dt[...]` fields;
- add missing reusable operators to both `code/stock1800/feature.py` and
  `group_work/01_feature_engineering/custom_operators.py` when needed;
- implement the factor as `factor_xx_descriptive_name(dt, ...)` in
  `group_work/factor_lib/factors.py`;
- add it to `FACTOR_REGISTRY`;
- document whether it is exact, proxy, or blocked;
- run the single-factor evaluator when possible.

Prefer exact implementations. Use proxy implementations only when the source
field is absent but a reasonable local substitute exists. When using a proxy,
document the substitution clearly in code comments or docstrings and in the
progress file.

Do not silently invent unavailable data.

Use conda bishe as python environment. Use pip install to install packages you need.

## Verification Command

For an implemented factor key:

```powershell
conda run -n bishe python group_work\02_factor_calculation\evaluate_factor.py --factor <factor_key>
```

If the command fails due to environment/sandbox issues, record the environment
failure separately from factor-code failure. Do not mark the factor broken
unless the traceback points to the factor implementation or field mapping.

