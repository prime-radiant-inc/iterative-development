---
name: iterative-development
description: Use when implementing a project with a large, comprehensive, or ambiguous spec — extracts requirements with proof obligations, defines a walking skeleton with its first journey scenario, then loops through audited sprints that continuously build a behavior evidence corpus. Completion means passing evidence, not just finished stories.
---

# Iterative Development

## Overview

Orchestrator for the iterative-development plugin. Drives the full autonomous lifecycle: extract requirements with proof obligations and behavior scenarios from human spec collateral, define a walking skeleton that passes its first journey scenario, then loop through audited sprints that continuously build a reusable behavior evidence corpus. Completion means the product has passing behavior evidence at the correct seam for every externally observable requirement — not just that stories are marked done. Every evaluative gate uses parallel adversarial review (PAR).

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
   - Chunks the spec, classifies by taxonomy (journeys → E2E, domains → integration, etc.)
   - Dispatches parallel extraction subagents that produce stories with proof obligations AND behavior scenarios
   - Aggregates stories into per-epic files, scenarios into behavior-scenarios.md
   - Builds coverage ledger with both story AND scenario coverage
   - Produces `docs/superpowers/iterations/requirements/`, `docs/superpowers/iterations/behavior-scenarios.md`, `docs/superpowers/iterations/behavior-corpus.md`
3. Invoke `scoping-the-simplest-core` on the resulting backlog.
   - Defines the walking skeleton iteration (ITER-0000) + ordered follow-on iterations
   - Runs citation check + PAR scope review
   - Produces `docs/superpowers/iterations/roadmap.md`
   - Walking skeleton must close at least one journey scenario (not just compile)
   - Applies story splitting when stories have heterogeneous-dependency ACs

### Main loop

```
while True:
    check_for_human_interrupt()

    if not roadmap has pending iterations:
        if last audit was clean:
            run final behavior-evidence audit (see below)
            if behavior audit clean:
                break  # done
            # else: audit found uncovered surfaces or weak evidence, new iterations added
        # else: audit found gaps, new iterations were added, continue

    run next iteration:
        - running-an-iteration (sentinel baseline → scope review → decompose code + evidence tasks → implementing-tasks → impacted + sentinel scenario runs → wrap up)
    
    audit:
        - auditing-progress (PAR paired auditors, three-tier: deep evidence + impacted behavior + sentinel corpus)
        - if gaps: append to backlog, revise roadmap, continue
        - if clean: mark last_audit_clean, continue
```

### Final behavior-evidence audit

Before declaring the project complete, verify that the product has adequate behavior evidence — not just that all stories are marked done:

1. List every major user-facing surface from the original spec (settings panes, UI flows, CLI commands, journeys, etc.)
2. For each surface, verify that:
   - Corresponding stories exist AND are implemented
   - Corresponding scenarios exist AND have passing evidence at the correct seam
   - Journey scenarios that cross multiple surfaces are passing E2E
3. Check the behavior corpus index for completeness:
   - Every journey spec file has at least one JOURNEY-NNNN scenario
   - Every scenario has a non-TBD execution command
   - All sentinel scenarios pass
4. Flag any surface with:
   - No corresponding story (extraction under-scoped)
   - No corresponding scenario (evidence gap)
   - Evidence at a weaker seam than the requirement demands
   - Manual-residual scenarios that could be automated
5. If gaps found: create new stories/scenarios/iterations, continue the loop

The final question is: "Can the system point to passing behavior evidence for every externally observable requirement the spec describes?" Not: "Are the stories done?"

### Resume (re-invocation with existing state)

All process state lives in three artifact files:
- `docs/superpowers/iterations/requirements/` (backlog with story status)
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

## Skill Precedence

When running autonomously, this orchestrator takes precedence over interactive-gate skills (e.g., `brainstorming` which requires design approval before implementation). The iterative-development process has its own design gates (scope review, PAR) that replace interactive approval. Do not block on skills that assume a human is present to approve each step.

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
| Extract | `extracting-requirements` | Chunk → parallel extract → aggregate → `requirements/` |
| Scope | `scoping-the-simplest-core` | Walking skeleton + iterations → `roadmap.md` (with PAR scope review) |
| Implement | `running-an-iteration` | Scope review → decompose → `implementing-tasks` → wrap up |
| Task execution | `implementing-tasks` | Per-task: implementer → PAR spec review → PAR quality review |
| Audit | `auditing-progress` | PAR paired auditors, two-tier (deep + sweep) |

## Artifact Location

All plugin artifacts live in `docs/superpowers/iterations/`. Never modify the human's spec collateral.

| File | Purpose |
|---|---|
| `requirements/` | Backlog: story cards + epics with stable IDs and proof obligations |
| `behavior-scenarios.md` | Behavior contracts: reusable scenario cards with stable IDs |
| `behavior-corpus.md` | Execution index: scenario → seam → cadence → command |
| `roadmap.md` | Sprint plan: ordered iterations with impacted scenarios |
| `iteration-log.md` | Sprint history: what each iteration delivered + scenarios added |

## Quality Gates

Every evaluative gate uses parallel adversarial review (PAR):
- Pre-iteration scope review (citation + scope-creep + boxing-in + scenario coverage + story splitting)
- Pre-iteration sentinel corpus baseline
- Per-task spec-compliance review with evidence quality check
- Per-task code-quality review with boxing-in + corpus contribution check
- Post-iteration impacted + sentinel scenario runs
- Per-sprint audit (deep evidence + impacted behavior + sentinel corpus)

See `skills/shared/parallel-adversarial-review.md` for PAR methodology.
