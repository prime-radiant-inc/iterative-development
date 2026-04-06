---
name: scoping-the-simplest-core
description: Use when turning a requirements-index.md into a roadmap — selects the walking skeleton iteration and orders the remaining work into follow-on iterations that can each be delivered as a single sprint.
---

# Scoping the Simplest Core

## Overview

Reads `docs/superpowers/iterations/requirements-index.md` and produces `docs/superpowers/iterations/roadmap.md`: a walking-skeleton iteration (ITER-0000) plus ordered follow-on iterations. Runs citation and scope review via PAR before committing the roadmap.

## When to Use

Invoked by `iterative-development` during bootstrap after `extracting-requirements`.

## Scoping Process

### 1. Read the backlog

Read `docs/superpowers/iterations/requirements-index.md` — epic summaries and story titles first, then dip into ACs when selecting.

### 2. Define the walking skeleton (ITER-0000)

Select a small cohesive set of stories from as many distinct epics as possible. The walking skeleton should prove the end-to-end shape of the product works. Selection rule: "if someone ran just these stories, they should see a demo that proves the product exists."

### 3. Order remaining stories into iterations

Each iteration is a sprint's worth of cohesive work. Iteration granularity is judgment-based — no hardcoded story count.

### 4. Run citation check

Run: `python3 scripts/check_citations.py docs/superpowers/iterations/roadmap.md docs/superpowers/iterations/requirements-index.md`

Every iteration must cite only valid STORY-IDs from the index.

### 5. Scope review via PAR

Following `skills/shared/parallel-adversarial-review.md`:

1. Build scope reviewer prompts using `skills/running-an-iteration/scope-reviewer-prompt.md`
2. Wrap in PAR competitive framing
3. Dispatch paired scope reviewers focused on:
   - Is ITER-0000 really the thinnest possible walking skeleton?
   - Could anything be deferred from ITER-0000 to a follow-on?
   - Does ITER-0000's design box in any follow-on iteration?
4. If REVISE recommended: adjust and re-review until APPROVE

### 6. Write and validate roadmap

Write the result to `docs/superpowers/iterations/roadmap.md` following the format in `tests/fixtures/roadmap.example.md`.

Run: `python3 scripts/validate_artifact.py --type roadmap docs/superpowers/iterations/roadmap.md`

### 7. Commit

```bash
git add docs/superpowers/iterations/roadmap.md
git commit -m "docs: add roadmap.md — walking skeleton + iteration plan"
```

## Quick Reference

| Step | Tool/Skill | Purpose |
|---|---|---|
| Citation check | `scripts/check_citations.py` | All cited stories exist |
| Scope review | PAR + scope reviewer prompt | Walking skeleton is minimal, no boxing-in |
| Validate | `scripts/validate_artifact.py --type roadmap` | Format check |

## References

- `skills/shared/parallel-adversarial-review.md` — PAR methodology
- `skills/running-an-iteration/scope-reviewer-prompt.md` — scope reviewer prompt (reused)
- `scripts/check_citations.py` — mechanical citation check
