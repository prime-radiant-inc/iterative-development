---
name: scoping-the-simplest-core
description: Use when turning a requirements-index.md into a roadmap — selects the walking skeleton iteration and orders the remaining work into follow-on iterations that can each be delivered as a single sprint.
---

# Scoping the Simplest Core

## Overview

Reads `docs/superpowers/iterations/requirements-index.md` and produces `docs/superpowers/iterations/roadmap.md`: a walking-skeleton iteration (ITER-0000) plus an ordered list of follow-on iterations that each commit to a cohesive subset of stories.

**This is Plan 1 — walking skeleton implementation. Parallel adversarial scope review, boxing-in look-ahead, and formal walking-skeleton selection heuristics are NOT yet implemented and will be added in later plans.**

## When to Use

Invoked by `iterative-development` during bootstrap after `extracting-requirements` has produced the backlog.

## Walking Skeleton Behavior (Plan 1)

1. Read `docs/superpowers/iterations/requirements-index.md`.
2. Define the walking-skeleton iteration (ITER-0000):
   - Select a small cohesive set of stories (for trivial specs in Plan 1, this may be the ENTIRE backlog)
   - The walking skeleton should prove the end-to-end shape of the product works
3. Order the remaining stories into follow-on iterations. For Plan 1 dogfood, a trivial spec may have zero follow-on iterations.
4. Write the result to `docs/superpowers/iterations/roadmap.md` following the format in `tests/fixtures/roadmap.example.md`.
5. Run `scripts/validate_artifact.py --type roadmap <path>` to verify the output is well-formed.
6. If validation fails, fix the formatting issues and re-validate.

## Quick Reference

| Input | Output | Validator |
|---|---|---|
| `requirements-index.md` | `roadmap.md` | `scripts/validate_artifact.py --type roadmap` |

## Deferred to later plans

Parallel adversarial scope review, citation integrity check (mechanically), boxing-in look-ahead against next 3 iterations, formal walking-skeleton selection heuristic beyond "cross-cut epics", user-tunable iteration granularity.
