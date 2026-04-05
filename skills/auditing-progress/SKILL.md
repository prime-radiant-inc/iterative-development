---
name: auditing-progress
description: Use when an iteration has just finished and you need to verify the just-delivered work matches its story acceptance criteria and the whole product has no regressions — runs after every iteration as part of the planning cycle.
---

# Auditing Progress

## Overview

Runs after every iteration. Deep-checks the just-finished iteration's work (every AC verified by running tests + reading code) and lightly sanity-sweeps the whole product for regressions. Returns gaps (ACs not actually met) and unrequested features (code that doesn't map to any story).

**This is Plan 1 — walking skeleton implementation. Parallel adversarial auditor pairs, two-tier partitioning (deep + sweep), per-epic auditor dispatch, and sophisticated unrequested-feature scanning are NOT yet implemented and will be added in later plans.**

## When to Use

Invoked by `iterative-development` after every `running-an-iteration` call, before picking the next iteration.

## Walking Skeleton Behavior (Plan 1)

1. Read `docs/superpowers/iterations/requirements-index.md`.
2. Identify the stories that were marked `done:ITER-<current>` in the just-finished iteration.
3. Dispatch a single auditor subagent (no parallel pairs, no partitioning) with:
   - The list of just-done stories and their acceptance criteria
   - The current product state (file paths, test command)
   - Instructions to: run the tests for each AC, verify the AC is actually met, flag any that are not
4. The auditor returns a gap list:
   - For each just-done story, which ACs pass and which fail
5. For Plan 1 walking skeleton: **no sweep tier**. Only the just-done stories are audited. Regression detection across earlier work is deferred to Plan 4.
6. Aggregate the auditor's report:
   - If any ACs fail: append gap stories to `requirements-index.md` (status `pending`) and revise `roadmap.md` to add a follow-up iteration
   - If all ACs pass: the iteration is confirmed done, proceed to the next iteration
7. Return the audit result to the orchestrator.

## Quick Reference

| Reads | Writes | Dispatches |
|---|---|---|
| `requirements-index.md`, product code/tests | `requirements-index.md` (gap stories), `roadmap.md` (new iteration) if gaps | Auditor subagent (one, non-paired) |

## Deferred to later plans

Parallel adversarial auditor pairs, two-tier scope (deep new work + light whole-product sweep), per-epic partitioning for large backlogs, unrequested-feature scanning across iteration diffs, formal aggregation rules for disagreeing auditor findings.
