---
name: running-an-iteration
description: Use when executing the next pending iteration from an iterative-development roadmap — picks the iteration, decomposes into code and evidence tasks, runs sentinel corpus baseline, dispatches implementing-tasks, runs impacted + sentinel scenarios, and updates artifacts.
---

# Running an Iteration

## Overview

Drives one iteration: picks the next pending, runs sentinel corpus baseline, runs pre-iteration scope review via PAR, decomposes into code and evidence tasks, dispatches `implementing-tasks`, runs impacted + sentinel scenarios at wrap-up, and updates the roadmap and iteration log.

## When to Use

Invoked by `iterative-development` inside the main loop. Each invocation runs exactly one iteration. After return, the orchestrator invokes `auditing-progress`.

## Script Location

All scripts referenced below live in this skill's `scripts/` directory, next to this SKILL.md file.

## Iteration Process

### 1. Pick next iteration

Read `docs/superpowers/iterations/roadmap.md`, find the first iteration with status `pending`.

### 2. Load scope context

Read the per-epic files in `docs/superpowers/iterations/requirements/` to load the full story cards for each committed story ID. Only read the epic files that contain stories for this iteration — not all of them. Also:
- Load the next 3 pending iterations from the roadmap for look-ahead
- Read `docs/superpowers/iterations/behavior-scenarios.md` to identify impacted scenarios
- Read `docs/superpowers/iterations/behavior-corpus.md` to identify sentinel scenarios

### 3. Run sentinel corpus baseline

Before any code changes, run every scenario in the behavior corpus with run cadence `sentinel`:

- If all sentinels pass: record baseline as clean, proceed
- If any sentinel fails: the failure predates this iteration. Record it, create a gap story for it, but proceed with the iteration (the gap will be addressed in a follow-up)

This establishes whether regressions exist before the current iteration starts.

### 4. Pre-iteration consistency audit

Before planning any work, verify that artifact state is consistent:

1. **Citation check:** `python3 "scripts/check_citations.py" docs/superpowers/iterations/roadmap.md docs/superpowers/iterations/requirements/` — if citations fail, stop and fix the roadmap.
2. **Status reconciliation:** For each story in this iteration's scope, verify:
   - Stories listed in the roadmap iteration are not already marked `done:ITER-XXXX` in the requirements index (unless code/tests actually exist for them)
   - Stories marked `done` in the requirements index actually have corresponding code and tests
   - No story appears in multiple pending iterations
3. **Epic counter validation:** Spot-check that epic progress counters match the actual count of `done` stories.

If any inconsistencies are found, reconcile before proceeding. Do not trust any single artifact blindly — cross-check.

### 5. Pre-iteration scope review (PAR)

Following `skills/shared/parallel-adversarial-review.md`:

1. Build the scope reviewer prompt using `scope-reviewer-prompt.md`
2. Wrap in PAR competitive framing from `skills/shared/par-reviewer-wrapper.md`
3. Dispatch TWO scope reviewers in parallel (Agent tool, two calls in one message)
4. Aggregate findings: same issue from both = high confidence, unique = still actionable, severity disagreement = take worst
5. If REVISE recommended: adjust iteration scope and re-review. Loop until APPROVE.

### 6. Decompose into code tasks AND evidence tasks

Break the iteration scope into TDD-sized tasks. Each task = failing test → implementation → passing test → commit.

**Evidence tasks:** In addition to code tasks, identify:
- Which existing scenarios are impacted by this iteration's changes
- Which new scenarios must be added (from the story proof obligations)
- Which scenario harnesses need to be extended
- Which behavior corpus entries need updated execution commands

Evidence tasks are first-class — they produce scenario updates, test harness extensions, and corpus index entries. They are NOT afterthoughts. Interleave evidence tasks with code tasks: after implementing a feature, the next task should be extending or adding the scenario that proves it.

**Cross-iteration dependencies:** Some stories reference subsystems that don't exist yet. For these, implement a protocol/abstraction that satisfies the story's ACs without coupling to the future implementation. Document the dependency with a TODO comment citing the future iteration. Do NOT defer the story silently or force premature integration.

### 7. Dispatch implementing-tasks

Pass the task list (code + evidence tasks) and iteration context to `implementing-tasks`. Wait for completion.

### 8. Post-iteration scenario runs

After all tasks complete, run:

1. **Impacted scenarios:** every scenario in the behavior corpus whose owning stories were touched by this iteration
2. **Sentinel scenarios:** every scenario with run cadence `sentinel`

If any impacted or sentinel scenario fails that passed at baseline (step 3), this iteration introduced a regression. Create a fix task and re-dispatch to `implementing-tasks`.

### 9. Wrap up

- Verify all iteration stories' ACs pass (sanity check before audit)
- Verify all proof obligations for observable ACs have corresponding scenario evidence
- Mark stories `done:ITER-NNNN` in the relevant epic files under `requirements/`
- Update scenario automation status and execution commands in `behavior-scenarios.md`
- Update the behavior corpus index in `behavior-corpus.md`
- Update iteration status in `roadmap.md` to `done`
- Append entry to `docs/superpowers/iterations/iteration-log.md` — include:
  - Stories delivered
  - Scenarios added or updated
  - Sentinel corpus results
- Validate: `python3 "scripts/validate_iteration_log.py" docs/superpowers/iterations/iteration-log.md`
- Return control to orchestrator (do NOT invoke `auditing-progress` — that's the orchestrator's job)

## Quick Reference

| Step | Tool/Skill | Purpose |
|---|---|---|
| Sentinel baseline | Run sentinel scenarios | Establish pre-iteration regression state |
| Citation check | `scripts/check_citations.py` | Mechanical: cited stories exist |
| Scope review | PAR + `scope-reviewer-prompt.md` | Semantic: scope, scenarios, splitting, boxing-in |
| Task execution | `implementing-tasks` | TDD code + evidence implementation |
| Post-iteration runs | Run impacted + sentinel scenarios | Catch regressions |
| Wrap up | `scripts/validate_iteration_log.py` | Artifact validation |

## References

- `skills/shared/parallel-adversarial-review.md` — PAR methodology
- `skills/shared/behavior-evidence-formats.md` — scenario and proof obligation formats
- `scope-reviewer-prompt.md` — scope reviewer prompt template
- `scripts/check_citations.py` — mechanical citation check
