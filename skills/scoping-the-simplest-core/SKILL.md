---
name: scoping-the-simplest-core
description: Use when turning extracted requirements into a roadmap — selects the walking skeleton iteration with its first journey scenario, orders remaining work into follow-on iterations, and applies story splitting when ACs have different dependency profiles.
---

# Scoping the Simplest Core

## Overview

Reads the per-epic requirement files in `docs/superpowers/iterations/requirements/` and `docs/superpowers/iterations/behavior-scenarios.md`, and produces `docs/superpowers/iterations/roadmap.md`: a walking-skeleton iteration (ITER-0000) plus ordered follow-on iterations. The walking skeleton must produce the first runnable journey scenario. Runs citation and scope review via PAR before committing the roadmap.

## When to Use

Invoked by `iterative-development` during bootstrap after `extracting-requirements`.

## Script Location

All scripts referenced below live in this skill's `scripts/` directory, next to this SKILL.md file.

## Scoping Process

### 1. Read the backlog

Read the epic files in `docs/superpowers/iterations/requirements/` — scan epic headers and story titles first, then dip into specific epic files for ACs when selecting.

Also read `docs/superpowers/iterations/behavior-scenarios.md` to understand which scenarios exist and which stories they cover.

### 2. Define the walking skeleton (ITER-0000)

Select a small cohesive set of stories from as many distinct epics as possible. The walking skeleton should prove the end-to-end shape of the product works.

**Scenario requirement:** the walking skeleton MUST include stories that close at least ONE journey scenario chain. Prefer the core product journey (e.g., "normal dictation" over "debug investigation"). The skeleton is not done until that journey scenario is runnable as an automated or scripted-reproducible test.

The walking skeleton must also produce:
- The first stable scenario IDs
- The first executable behavior harness (the E2E test infrastructure)
- A small sentinel corpus that can be rerun every iteration

**Harness-first task:** The walking skeleton's FIRST task should be designing and building the E2E test harness — before implementing any product features. Use the test infrastructure checklist in `skills/shared/behavior-evidence-formats.md` to guide the design. Document the harness design decisions in the project's docs. The harness is a first-class deliverable, not an afterthought — every subsequent iteration extends it.

Selection rule: "if someone ran just these stories, they should see a demo that proves the product exists AND have at least one passing journey scenario that proves the demo works."

### 3. Order remaining stories into iterations

Each iteration is a sprint's worth of cohesive work. Iteration granularity is judgment-based — no hardcoded story count.

**Story splitting rule:** when assigning stories to iterations, check each story's ACs for dependency profiles. If a story has ACs where:
- Some ACs can be satisfied in iteration N (their dependencies exist)
- Other ACs require subsystems from iteration N+M (their dependencies don't exist yet)

Then SPLIT the story:
1. Create a version with only the satisfiable ACs for iteration N
2. Create a version with the remaining ACs for iteration N+M
3. Update the requirements index with both versions (append `a`/`b` to the story ID)
4. Update scenario refs in both versions

**Why this matters:** moving a whole story to a later iteration because one AC has a late dependency causes the other ACs to be re-interpreted through the receiving iteration's theme, and they get silently dropped.

### 4. Run citation check

Run: `python3 "scripts/check_citations.py" docs/superpowers/iterations/roadmap.md docs/superpowers/iterations/requirements/`

Every iteration must cite only valid STORY-IDs from the index.

### 5. Scope review via PAR

Following `skills/shared/parallel-adversarial-review.md`:

1. Build scope reviewer prompts using `skills/running-an-iteration/scope-reviewer-prompt.md`
2. Wrap in PAR competitive framing
3. Dispatch paired scope reviewers focused on:
   - Is ITER-0000 really the thinnest possible walking skeleton?
   - Does ITER-0000 close at least one journey scenario?
   - Could anything be deferred from ITER-0000 to a follow-on?
   - Does ITER-0000's design box in any follow-on iteration?
   - Are any stories over-broad (mixing skeleton-level concerns with later integrations)?
   - **Are there stories with heterogeneous-dependency ACs that should be split?**
   - **Does any iteration leave observable behavior without planned scenario coverage?**
4. **If stories need splitting:** apply the splitting rule from step 3, update requirements, re-scope.
5. If REVISE recommended: adjust and re-review until APPROVE

### 6. Write and validate roadmap

Write the result to `docs/superpowers/iterations/roadmap.md` using this format:

```
# Roadmap

## Walking skeleton (ITER-0000)

**Intent:** <one-line description of the thinnest end-to-end slice>
**Design rationale:** <why these stories, what they prove together>
**Journey scenario:** <JOURNEY-NNNN that the skeleton must pass>
**Stories committed:**
- STORY-NNNN (EPIC-NNN)
- ...
**Status:** pending

## Iteration list

### ITER-0001 — <name>

**Stories:** STORY-NNNN, STORY-NNNN, ...
**Rationale:** <why these stories belong together>
**Status:** pending
**Impacted scenarios:** <SCENARIO-NNNN, JOURNEY-NNNN that this iteration touches>
**Look-ahead check:** <does this block or get blocked by neighbors?>
```

Run: `python3 "scripts/validate_roadmap.py" docs/superpowers/iterations/roadmap.md`

**Note:** The validator checks format only. The PAR scope review is the real structural gate.

### 7. Commit

```bash
git add docs/superpowers/iterations/roadmap.md
git commit -m "docs: add roadmap — walking skeleton with journey scenario + iteration plan"
```

## Quick Reference

| Step | Tool/Skill | Purpose |
|---|---|---|
| Citation check | `scripts/check_citations.py` | All cited stories exist |
| Scope review | PAR + scope reviewer prompt | Walking skeleton minimal, journey scenario included, story splitting applied, no boxing-in |
| Story splitting | Manual (if PAR or dependency analysis finds heterogeneous ACs) | Split stories by dependency profile |
| Validate | `scripts/validate_roadmap.py` | Format check only |

## References

- `skills/shared/parallel-adversarial-review.md` — PAR methodology
- `skills/shared/behavior-evidence-formats.md` — scenario and proof obligation formats
- `skills/running-an-iteration/scope-reviewer-prompt.md` — scope reviewer prompt (reused)
- `scripts/check_citations.py` — mechanical citation check
