# Mission: Implement Source Factors

## Goal

Implement every factor described in the repo-root source folder whose name ends
with `365_cleaned/`, as far as local data allows. By the end, the user should be
able to open `group_work/FACTOR_IMPLEMENTATION_PROGRESS.md` and immediately see:

- which factors were successfully implemented and tested;
- which factors are implemented as proxies;
- which factors are blocked because data is missing but easy to add;
- which factors are blocked because current local data cannot support them.

## Important Starting Point

Read `AGENTS.md` first. It authorizes native Codex subagents through
`spawn_agent` and forbids using the `opencode-subagent` skill for this mission.

Then read `PROJECT_AGENT_GUIDE.md`. It explains which files matter and which
large/irrelevant files to skip.

## Phase 1: Understand Project Rules

Read these files and keep notes compact:

1. `PROJECT_AGENT_GUIDE.md`
2. `group_work/README.md`
3. `group_work/01_feature_engineering/factor_formulas.md`
4. `group_work/01_feature_engineering/custom_operators.py`
5. `code/stock1800/feature.py`
6. `group_work/factor_lib/factors.py`
7. `group_work/factor_lib/data_loader.py`
8. `group_work/02_factor_calculation/evaluate_factor.py`
9. `group_work/FACTOR_IMPLEMENTATION_PROGRESS.md`

Key rules to learn:

- factor functions live in `group_work/factor_lib/factors.py`;
- runtime operators are imported from `code/stock1800/feature.py`;
- `custom_operators.py` documents stage-1 custom operators and should stay in
  sync with new reusable operators;
- factor keys must be added to `FACTOR_REGISTRY`;
- single-factor testing uses
  `group_work/02_factor_calculation/evaluate_factor.py`;
- `stage2_factor_screening.py` is incomplete and not needed for individual
  factor implementation.

## Phase 2: Inventory Current Coverage

Build a current inventory before editing:

1. List all source files under the repo-root `*365_cleaned/` folder.
2. List all existing `factor_xx_*` functions in `group_work/factor_lib/factors.py`.
3. List all keys in `FACTOR_REGISTRY`.
4. Compare source factor IDs against implemented/registered IDs.
5. Update `group_work/FACTOR_IMPLEMENTATION_PROGRESS.md` with the inventory
   result before implementing new factors.

Do not assume that a formula documented in `factor_formulas.md` is already
implemented. Verify the function and registry entry.

## Phase 3: Implement Factors

For each missing or incomplete factor:

1. Read the corresponding source markdown in the repo-root `*365_cleaned/`
   folder.
2. Extract the formula, field names, and intended economic meaning.
3. Check whether each source field exists locally:
   - first in `data_1800/stock1000/data/matrix/`;
   - then in `data_1800/stock1000/data/finTTM/`;
   - then in loader-supported fields in `data_loader.py`;
   - avoid broad data scans unless needed.
4. Choose one of four outcomes:
   - `success`: exact enough implementation using local data;
   - `proxy`: reasonable local substitute, documented clearly;
   - `missing_easy`: source field missing, but easy to add if user provides or
     generates a clear data file;
   - `missing_unsolved`: source field missing and cannot be credibly inferred
     from current local data.
5. If implementing:
   - add or reuse operators in `code/stock1800/feature.py`;
   - mirror new reusable operators in
     `group_work/01_feature_engineering/custom_operators.py`;
   - add the factor function in `group_work/factor_lib/factors.py`;
   - add it to `FACTOR_REGISTRY`;
   - update `factor_formulas.md` if the formula/status needs correction;
   - update the progress file immediately.

## Phase 4: Test Implemented Factors

For each implemented or proxy factor, run:

```powershell
conda run -n bishe python group_work\02_factor_calculation\evaluate_factor.py --factor <factor_key>
```

Record in `group_work/FACTOR_IMPLEMENTATION_PROGRESS.md`:

- command run;
- pass/fail;
- metrics path if generated;
- any traceback summary if failed;
- whether failure is environment-related or factor-related.

If many factors are implemented, test in batches but still record per-factor
status.

## Phase 5: Use Subagents When Helpful

The user authorized native Codex subagents. Good split:

- Worker A: factors 01-14
- Worker B: factors 15-28
- Worker C: factors 29-42
- Worker D: factors 43-56
- Explorer: local data fields and existing operator coverage

Adjust ranges based on what is already implemented. Workers should edit only
their assigned factor functions and progress rows. The main agent integrates,
tests, and resolves conflicts.

Do not use Opencode or the `opencode-subagent` skill.

## Phase 6: Final Deliverables

Before stopping, ensure these are true:

- every factor ID 01-56 has a row in
  `group_work/FACTOR_IMPLEMENTATION_PROGRESS.md`;
- every row has one of `success`, `proxy`, `missing_easy`,
  `missing_unsolved`, or `not_tested`;
- all implemented factors are present in `FACTOR_REGISTRY`;
- new operators are in both runtime and stage-1 documentation locations;
- tests were run or test blockers were recorded;
- the final response tells the user where to read the progress file.

Do not stop while factors remain untriaged unless the user interrupts or a
real blocker requires user input.

