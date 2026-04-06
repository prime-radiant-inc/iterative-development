---
name: iterative-development
description: Use when implementing a project with a large, comprehensive, or ambiguous spec that would overwhelm the writing-plans → subagent-driven-development flow — extracts requirements, defines a walking skeleton, then loops through audited sprints autonomously.
---

# Iterative Development

## Overview

Orchestrator for the iterative-development plugin. Drives the full autonomous lifecycle: extract requirements from human spec collateral, define a walking skeleton, loop through audited sprints until an auditor confirms the product matches the backlog. Every evaluative gate uses parallel adversarial review (PAR).

This is an alternative to `superpowers:writing-plans → superpowers:subagent-driven-development` for projects where the upfront-planning approach would lose the plot.

## When to Use

- Spec is large, comprehensive, or ambiguous (10+ files, 100+ requirements)
- You need the product to be in a working, testable state at every iteration boundary
- You want an autonomous audited loop rather than a single upfront plan
- The writing-plans flow has lost the plot on this project before

Do NOT use for small, bounded projects — `superpowers:writing-plans → superpowers:subagent-driven-development` is simpler and more appropriate.

## The Autonomous Loop

### Bootstrap (first invocation)

1. Check `docs/superpowers/iterations/` for existing state. If found, skip to **Resume** below.
2. Invoke `extracting-requirements` on the human-provided spec path.
   - Chunks the spec via `scripts/chunk_spec.py`, dispatches parallel extraction subagents, aggregates via `scripts/aggregate_stories.py`
   - Produces `docs/superpowers/iterations/requirements-index.md`
3. Invoke `scoping-the-simplest-core` on the resulting backlog.
   - Defines the walking skeleton iteration (ITER-0000) + ordered follow-on iterations
   - Runs citation check + PAR scope review
   - Produces `docs/superpowers/iterations/roadmap.md`

### Main loop

```
while True:
    check_for_human_interrupt()

    if not roadmap has pending iterations:
        if last audit was clean:
            break  # done
        # else: audit found gaps, new iterations were added, continue

    run next iteration:
        - running-an-iteration (scope review → decompose → implementing-tasks → wrap up)
    
    audit:
        - auditing-progress (PAR paired auditors, two-tier: deep new + sweep whole)
        - if gaps: append to backlog, revise roadmap, continue
        - if clean: mark last_audit_clean, continue
```

### Resume (re-invocation with existing state)

All process state lives in three artifact files:
- `docs/superpowers/iterations/requirements-index.md` (backlog with story status)
- `docs/superpowers/iterations/roadmap.md` (iteration plan with status)
- `docs/superpowers/iterations/iteration-log.md` (completed iteration history)

On re-invocation: read `roadmap.md`, find the next pending iteration, and continue from there. There is no ephemeral in-memory state to recover. The command "continue iterative development with the existing plan" always works.

If the orchestrator crashed mid-iteration, the partially-completed iteration's git commits are preserved. On resume, the next un-started iteration picks up. If the in-progress iteration left the code in a broken state, treat it as a gap — the audit will catch it and add corrective work.

## Human Interrupt Protocol

The loop runs without human intervention. The only way the human injects new information mid-run is by interrupting between iterations.

**How it works:**
- The human types the update into the chat session ("we dropped feature X", "the spec changed, re-read specs/foo.md", "add a new requirement for Y")
- The orchestrator notices the interrupt at the **next iteration boundary** — after the current iteration's audit completes, before the next iteration starts
- At the boundary: invoke `extracting-requirements` in incremental mode on the changed spec files, merge new/revised story cards into the backlog, revise the roadmap if changes invalidate downstream iterations, then resume

**Guarantees:**
- Changes during mid-iteration do NOT disrupt in-progress work. The current iteration completes first.
- The orchestrator never silently drops an interrupt. If ambiguous, ask for clarification before resuming.
- Existing story IDs are preserved across re-extraction. Removed stories flip to `deferred`, not deleted.

**What does NOT trigger interrupt processing:**
- The orchestrator does not poll the filesystem for spec changes
- The orchestrator does not ask "anything to change?" between iterations
- Human presence is not required at iteration boundaries

## Escalation Policy

**Catastrophe-only.** The loop is autonomous. Human escalation is reserved for total failure — the plugin cannot make any forward progress at all.

These do NOT trigger escalation:
- A reviewer finding issues (those become fix work)
- An audit finding gaps (those become new iterations)
- An implementer reporting BLOCKED on a task (try: more context, more capable model, smaller task)
- Ambiguity in the spec (make a reasonable judgment call, document it in the iteration log)
- Difficulty or slow progress (keep going)

The orchestrator does NOT prompt "should I continue?" between iterations.

## Skill Invocation Reference

| Phase | Skill | What it does |
|---|---|---|
| Extract | `extracting-requirements` | Chunk → parallel extract → aggregate → `requirements-index.md` |
| Scope | `scoping-the-simplest-core` | Walking skeleton + iterations → `roadmap.md` (with PAR scope review) |
| Implement | `running-an-iteration` | Scope review → decompose → `implementing-tasks` → wrap up |
| Task execution | `implementing-tasks` | Per-task: implementer → PAR spec review → PAR quality review |
| Audit | `auditing-progress` | PAR paired auditors, two-tier (deep + sweep) |

## Artifact Location

All plugin artifacts live in `docs/superpowers/iterations/`. Never modify the human's spec collateral.

| File | Purpose |
|---|---|
| `requirements-index.md` | Backlog: story cards + epics with stable IDs |
| `roadmap.md` | Sprint plan: ordered iterations with status |
| `iteration-log.md` | Sprint history: what each iteration delivered |

## Quality Gates

Every evaluative gate uses parallel adversarial review (PAR):
- Pre-iteration scope review (citation + scope-creep + boxing-in look-ahead)
- Per-task spec-compliance review
- Per-task code-quality review with boxing-in check
- Per-sprint audit (deep new work + sweep whole product)

See `skills/shared/parallel-adversarial-review.md` for PAR methodology.
