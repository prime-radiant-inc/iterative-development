---
name: iterative-development
description: Use when implementing a project with a large, comprehensive, or ambiguous spec that would overwhelm the writing-plans → subagent-driven-development flow — extracts requirements, defines a walking skeleton, then loops through audited sprints.
---

# Iterative Development

## Overview

Orchestrator for the iterative-development plugin. Drives the end-to-end lifecycle: extract requirements from human spec collateral, define a walking skeleton, loop through audited sprints until the product matches the backlog. This is an alternative to `superpowers:writing-plans → superpowers:subagent-driven-development` for projects where the upfront-planning approach would lose the plot.

**This is Plan 1 — walking skeleton implementation. Sophisticated behavior (parallel dispatch, parallel adversarial review, map-reduce extraction, two-tier audit) is NOT yet implemented and will be added in later plans.**

## When to Use

- Spec is large, comprehensive, or ambiguous (10+ files, 100+ requirements, or 50MB+ of prose)
- You need the product to be in a working, testable state at every iteration boundary
- You want an autonomous audited loop rather than a single upfront plan
- The writing-plans flow has lost the plot on this project before

Do NOT use for small, bounded projects — `superpowers:writing-plans → superpowers:subagent-driven-development` is simpler and more appropriate.

## Walking Skeleton Behavior (Plan 1)

For Plan 1, the orchestrator implements only the thinnest end-to-end threading. It:

1. Checks `docs/superpowers/iterations/` for existing state. If present, resume. If absent, bootstrap.
2. If bootstrapping:
   - Invoke `extracting-requirements` on the user-provided spec path
   - Invoke `scoping-the-simplest-core` on the resulting `requirements-index.md`
3. Loop (trivially, one iteration at a time):
   - Invoke `running-an-iteration`
   - Invoke `auditing-progress`
   - If audit finds gaps: append them to the backlog and loop
   - If roadmap is empty AND last audit clean: terminate
4. On termination, summarize what was delivered.

**Resume protocol:** on re-invocation with existing artifacts, read `roadmap.md`, find the next pending iteration, and continue from there.

**Human interrupts:** if the human says something like "spec changed" or "new requirements" between iterations, re-run `extracting-requirements` on the changed files and merge into the existing backlog. Do not poll for changes.

## Quick Reference

| Phase | Skill | Produces |
|---|---|---|
| Extract | `extracting-requirements` | `requirements-index.md` |
| Scope | `scoping-the-simplest-core` | `roadmap.md` |
| Implement | `running-an-iteration` → `implementing-tasks` | code commits + iteration log entry |
| Audit | `auditing-progress` | gaps or clean signal |

All plugin artifacts live in `docs/superpowers/iterations/`. Never modify the human's spec collateral.

## Deferred to later plans

Parallel adversarial review, map-reduce extraction, two-tier auditing, scope-review look-ahead, sophisticated roadmap revision, model selection rules.
