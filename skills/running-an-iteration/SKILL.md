---
name: running-an-iteration
description: Use when executing the next pending iteration from an iterative-development roadmap — picks the iteration, decomposes it into tasks, dispatches implementing-tasks, and updates the roadmap and iteration log.
---

# Running an Iteration

## Overview

Drives one iteration: picks the next pending, runs a pre-iteration scope review via PAR, decomposes into TDD tasks, dispatches `implementing-tasks`, and updates the roadmap and iteration log.

## When to Use

Invoked by `iterative-development` inside the main loop. Each invocation runs exactly one iteration. After return, the orchestrator invokes `auditing-progress`.

## Script Location

All scripts referenced below live in this skill's `scripts/` directory, next to this SKILL.md file.

## Iteration Process

### 1. Pick next iteration

Read `docs/superpowers/iterations/roadmap.md`, find the first iteration with status `pending`.

### 2. Load scope context

Read the per-epic files in `docs/superpowers/iterations/requirements/` to load the full story cards for each committed story ID. Only read the epic files that contain stories for this iteration — not all of them. Also load the next 3 pending iterations from the roadmap for look-ahead.

### 3. Pre-iteration consistency audit

Before planning any work, verify that artifact state is consistent:

1. **Citation check:** `python3 "scripts/check_citations.py" docs/superpowers/iterations/roadmap.md docs/superpowers/iterations/requirements/` — if citations fail, stop and fix the roadmap.
2. **Status reconciliation:** For each story in this iteration's scope, verify:
   - Stories listed in the roadmap iteration are not already marked `done:ITER-XXXX` in the requirements index (unless code/tests actually exist for them)
   - Stories marked `done` in the requirements index actually have corresponding code and tests
   - No story appears in multiple pending iterations
3. **Epic counter validation:** Spot-check that epic progress counters (e.g., "3/8 done") match the actual count of `done` stories in that epic. If they've drifted, fix them.

If any inconsistencies are found, reconcile before proceeding. Do not trust any single artifact blindly — cross-check.

### 4. Pre-iteration scope review (PAR)

Following `skills/shared/parallel-adversarial-review.md`:

1. Build the scope reviewer prompt using `scope-reviewer-prompt.md`
2. Wrap in PAR competitive framing from `skills/shared/par-reviewer-wrapper.md`
3. Dispatch TWO scope reviewers in parallel (Agent tool, two calls in one message)
4. Aggregate findings: same issue from both = high confidence, unique = still actionable, severity disagreement = take worst
5. If REVISE recommended: adjust iteration scope and re-review. Loop until APPROVE.

### 5. Decompose into tasks

Break the iteration scope into TDD-sized tasks. Each task = failing test → implementation → passing test → commit. Iteration granularity is judgment-based, not defaulted.

**Cross-iteration dependencies:** Some stories reference subsystems that don't exist yet (built in a later iteration). For these stories, implement a protocol/abstraction that satisfies the story's ACs without coupling to the future implementation. Document the dependency with a TODO comment citing the future iteration. Do NOT defer the story silently or force premature integration — build the interface now, wire the real implementation later.

### 6. Dispatch implementing-tasks

Pass the task list and iteration context to `implementing-tasks`. Wait for completion.

### 7. Wrap up

- Verify all iteration stories' ACs pass (sanity check before audit)
- Mark stories `done:ITER-NNNN` in the relevant epic files under `requirements/`
- Update iteration status in `roadmap.md` to `done`
- Append entry to `docs/superpowers/iterations/iteration-log.md`
- Validate: `python3 "scripts/validate_iteration_log.py" docs/superpowers/iterations/iteration-log.md`
- Return control to orchestrator (do NOT invoke `auditing-progress` — that's the orchestrator's job)

## Quick Reference

| Step | Tool/Skill | Purpose |
|---|---|---|
| Citation check | `scripts/check_citations.py` | Mechanical: cited stories exist |
| Scope review | PAR + `scope-reviewer-prompt.md` | Semantic: scope creep, boxing-in |
| Task execution | `implementing-tasks` | TDD implementation |
| Wrap up | `scripts/validate_iteration_log.py` | Artifact validation |

## References

- `skills/shared/parallel-adversarial-review.md` — PAR methodology
- `scope-reviewer-prompt.md` — scope reviewer prompt template
- `scripts/check_citations.py` — mechanical citation check
