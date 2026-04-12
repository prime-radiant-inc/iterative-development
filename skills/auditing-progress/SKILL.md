---
name: auditing-progress
description: Use when an iteration has just finished and you need to verify behavior evidence quality in three tiers — deep evidence for current stories, impacted behavior for touched scenarios, and sentinel corpus for high-value regression detection.
---

# Auditing Progress

## Overview

Runs after every iteration as part of the planning cycle. Verifies behavior evidence quality in three tiers using **parallel adversarial review (PAR)** — two paired auditor subagents evaluate the same work in parallel with competitive framing.

The audit answers: "Does durable, reusable evidence exist at the correct seam for every externally observable behavior this iteration touched?"

## When to Use

Invoked by `iterative-development` after every `running-an-iteration` call, before picking the next iteration.

## Audit Process

### 1. Partition the audit into three tiers

Read the per-epic requirement files in `docs/superpowers/iterations/requirements/`, `docs/superpowers/iterations/behavior-scenarios.md`, and `docs/superpowers/iterations/behavior-corpus.md`:

- **Tier 1 — Deep evidence:** stories marked `done:ITER-<current>` and scenarios added or updated in this iteration. Audit every AC and its proof obligation thoroughly.
- **Tier 2 — Impacted behavior:** all existing scenarios whose owning stories had code changes in this iteration (even if those stories were completed in earlier iterations). Verify the scenarios still pass.
- **Tier 3 — Sentinel corpus:** all scenarios with run cadence `sentinel` in the behavior corpus. Compare against the pre-iteration baseline from `running-an-iteration` step 3.

### 2. Dispatch paired auditor subagents (PAR)

Following the PAR methodology in `skills/shared/parallel-adversarial-review.md`:

1. Build the auditor prompt using `auditor-subagent-prompt.md`. Include ALL THREE tiers:
   - Tier 1: full story cards with proof obligations + new/changed scenario cards
   - Tier 2: impacted scenario cards + their current test results
   - Tier 3: sentinel scenario IDs + baseline results + current results
2. Wrap in competitive framing from `skills/shared/par-reviewer-wrapper.md`
3. Dispatch TWO auditor subagents in parallel
4. Wait for both to return

### 3. Aggregate findings

Following PAR aggregation rules:
- Same finding from both auditors → one finding, high confidence
- Finding from only one auditor → separate finding, still actionable
- Severity disagreement → take the more severe assessment, always fix it

### 4. Process results

- **If gaps found** (any AC fails, evidence is too weak, sentinel regression detected):
  - For AC failures: append gap stories to `requirements/` (status `pending`) or flip existing stories back from `done` to `pending`
  - For weak evidence: create evidence-improvement stories (add scenario, strengthen seam)
  - For sentinel regressions: create regression-fix stories with CRITICAL priority
  - Revise `roadmap.md` to add a follow-up iteration for the gaps
- **If clean** (all tiers pass, evidence is adequate):
  - The iteration is confirmed done
  - Return clean signal to the orchestrator

### 5. Return control

Return the audit result (clean or gaps) to the orchestrator. The orchestrator decides whether to loop or terminate.

## Quick Reference

| Tier | What it checks | Failure means |
|---|---|---|
| Deep evidence | Every AC + proof obligation for current iteration | Story not done, evidence too weak |
| Impacted behavior | Scenarios whose surfaces were touched | Stale or broken scenario |
| Sentinel corpus | High-value journey scenarios | Regression in previously-working behavior |

| Reads | Writes | Dispatches |
|---|---|---|
| `requirements/`, `behavior-scenarios.md`, `behavior-corpus.md`, product code/tests | `requirements/` (gaps), `roadmap.md` (new iteration) if gaps, `behavior-scenarios.md` (stale flags) | **Two** auditor subagents in parallel (PAR) |

## References

- `skills/shared/parallel-adversarial-review.md` — PAR methodology
- `skills/shared/par-reviewer-wrapper.md` — competitive framing wrapper
- `skills/shared/behavior-evidence-formats.md` — scenario and proof obligation formats
- `auditor-subagent-prompt.md` — auditor-specific prompt template
