---
name: auditing-progress
description: Use when an iteration has just finished and you need to verify the just-delivered work matches its story acceptance criteria and the whole product has no regressions — runs after every iteration as part of the planning cycle.
---

# Auditing Progress

## Overview

Runs after every iteration as part of the planning cycle. Verifies the just-finished iteration's work against story acceptance criteria and checks the whole product for regressions. Uses **parallel adversarial review (PAR)** — two paired auditor subagents evaluate the same work in parallel with competitive framing.

## When to Use

Invoked by `iterative-development` after every `running-an-iteration` call, before picking the next iteration.

## Audit Process

### 1. Partition the audit into two tiers

Read `docs/superpowers/iterations/requirements-index.md`:

- **Deep tier:** stories marked `done:ITER-<current>` — the ones this iteration just delivered. Audit every AC thoroughly.
- **Sweep tier:** all other stories previously marked `done:ITER-<earlier>`. Light sanity check — run test suites, spot-check ACs, look for regressions. Not a full re-verification.

### 2. Dispatch paired auditor subagents (PAR)

Following the PAR methodology in `skills/shared/parallel-adversarial-review.md`:

1. Build the auditor prompt using `auditor-subagent-prompt.md`. Include BOTH tiers:
   - Deep tier: paste full story cards with all ACs for just-done stories
   - Sweep tier: paste story IDs and test commands for previously-done stories (not full cards)
2. Wrap it in the competitive framing from `skills/shared/par-reviewer-wrapper.md`
3. Dispatch TWO auditor subagents in parallel (Agent tool, two calls in one message):
   - "PAR Review A: audit ITER-NNNN" with Reviewer [A]
   - "PAR Review B: audit ITER-NNNN" with Reviewer [B]
4. Wait for both to return

### 3. Aggregate findings

Following PAR aggregation rules:
- Same finding from both auditors → one finding, high confidence
- Finding from only one auditor → separate finding, still actionable
- Severity disagreement → take the more severe assessment, always fix it

### 4. Process results

- **If gaps found** (any AC fails in the aggregated report):
  - Append gap stories to `requirements-index.md` (status `pending`) or flip existing stories back from `done` to `pending`
  - Revise `roadmap.md` to add a follow-up iteration for the gaps
- **If clean** (all ACs pass, no unrequested features):
  - The iteration is confirmed done
  - Return clean signal to the orchestrator

### 5. Return control

Return the audit result (clean or gaps) to the orchestrator. The orchestrator decides whether to loop or terminate.

## Quick Reference

| Reads | Writes | Dispatches |
|---|---|---|
| `requirements-index.md`, product code/tests | `requirements-index.md` (gaps), `roadmap.md` (new iteration) if gaps | **Two** auditor subagents in parallel (PAR) |

## References

- `skills/shared/parallel-adversarial-review.md` — PAR methodology
- `skills/shared/par-reviewer-wrapper.md` — competitive framing wrapper
- `auditor-subagent-prompt.md` — auditor-specific prompt template

## Deferred to later plans

Two-tier scope (deep new work + light whole-product sweep), per-epic partitioning for large backlogs, unrequested-feature scanning across iteration diffs.
