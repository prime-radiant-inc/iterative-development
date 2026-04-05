---
name: running-an-iteration
description: Use when executing the next pending iteration from an iterative-development roadmap — picks the iteration, decomposes it into tasks, dispatches implementing-tasks, and updates the roadmap and iteration log.
---

# Running an Iteration

## Overview

Drives one iteration from the roadmap: picks the next pending iteration, decomposes its committed stories into TDD-sized tasks, dispatches `implementing-tasks` to execute them, and updates `roadmap.md` and `iteration-log.md`.

**This is Plan 1 — walking skeleton implementation. Pre-iteration scope review (citation check, adversarial review, boxing-in look-ahead), parallel adversarial review on tasks, and sophisticated wrap-up verification are NOT yet implemented and will be added in later plans.**

## When to Use

Invoked by `iterative-development` inside the main loop. Each invocation runs exactly one iteration. After return, the orchestrator invokes `auditing-progress` before picking the next iteration.

## Walking Skeleton Behavior (Plan 1)

1. Read `docs/superpowers/iterations/roadmap.md`, find the first iteration with status `pending`.
2. Read `docs/superpowers/iterations/requirements-index.md`, load the full story cards for each committed story ID in the iteration.
3. Decompose each story into TDD-sized tasks. Each task produces one failing test → minimal implementation → passing test → commit.
4. Dispatch `implementing-tasks` with the in-memory task list and the story context.
5. After `implementing-tasks` returns: for each story in the iteration, check that its acceptance criteria pass (run the tests). Flip each story's status in `requirements-index.md` from `pending` to `done:ITER-NNNN` where NNNN is the current iteration ID.
6. Update the iteration's status in `roadmap.md` from `pending` to `done`.
7. Append a new entry to `docs/superpowers/iterations/iteration-log.md` following the format in `tests/fixtures/iteration-log.example.md`:
   - Completed date
   - Stories delivered
   - Tasks executed count
   - Summary (one paragraph)
   - Learnings (if any)
   - Roadmap revisions (none for Plan 1)
8. Run `scripts/validate_artifact.py --type iteration-log <path>` to verify the log is well-formed.
9. Return control to the orchestrator. Do NOT invoke `auditing-progress` here — that is the orchestrator's job.

## Quick Reference

| Reads | Writes | Dispatches |
|---|---|---|
| `roadmap.md`, `requirements-index.md` | `requirements-index.md` (status), `roadmap.md` (status), `iteration-log.md` (append) | `implementing-tasks` |

## Deferred to later plans

Pre-iteration scope review (3 adversarial checks), formal story-to-task decomposition heuristics, parallel adversarial review wrappers around task dispatch, roadmap revision when iteration learnings invalidate downstream work.
