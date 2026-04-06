# Implementing-Tasks Full SDD Fork Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the walking-skeleton `implementing-tasks` stub (implementer-only, no reviews) with the full SDD fork: per-task two-stage review (spec compliance → code quality + boxing-in check), review re-dispatch loop, model selection guidance, and PAR on both review stages.

**Architecture:** Two new prompt templates (spec-compliance reviewer, code-quality reviewer with boxing-in check), plus a complete rewrite of `implementing-tasks/SKILL.md` that describes the full per-task cycle: dispatch implementer → PAR spec-compliance review → fix loop → PAR code-quality review → fix loop → mark complete. All review dispatches use the PAR machinery from Plan 3.

**Tech Stack:** Markdown (skills, prompts)

---

## File Structure

```
skills/
  implementing-tasks/
    SKILL.md                                # MODIFY: full SDD fork behavior
    implementer-subagent-prompt.md          # NEW: implementer dispatch template
    spec-compliance-reviewer-prompt.md      # NEW: spec-compliance review template
    code-quality-reviewer-prompt.md         # NEW: code-quality + boxing-in review template
```

---

### Task 1: Implementer subagent prompt template

**Files:**
- Create: `skills/implementing-tasks/implementer-subagent-prompt.md`

- [ ] **Step 1: Write the prompt template**

Create `skills/implementing-tasks/implementer-subagent-prompt.md`:

````markdown
# Implementer Subagent Prompt Template

Use this template when dispatching an implementer subagent for a single task.

```
Agent tool (general-purpose):
  description: "Implement: [task name]"
  prompt: |
    You are implementing a single task as part of an iterative development sprint.

    ## Task Description

    [FULL task description — what to build, what tests to write, what the
    acceptance criteria are. Paste the complete task, do not summarize.]

    ## Context

    [Which iteration this belongs to. Which story card(s) this task contributes
    to. Any architectural context or dependencies from earlier tasks.]

    ## Before You Begin

    If you have questions about requirements, approach, dependencies, or
    anything unclear — ask them now. It's always OK to pause and clarify.
    Don't guess or make assumptions.

    ## Your Job

    1. Follow TDD red-green-refactor (superpowers:test-driven-development):
       - Write the failing test first
       - Run it to verify it fails
       - Write the minimal implementation to make it pass
       - Run to verify it passes
       - Refactor if needed
    2. Commit your work when tests pass
    3. Self-review before reporting (see below)
    4. Report back with status

    ## Self-Review Checklist

    Before reporting, ask yourself:
    - Did I implement exactly what was specified? (nothing more, nothing less)
    - Are names clear and domain-appropriate?
    - Did I follow TDD discipline? (test before implementation)
    - Do tests verify real behavior, not mock behavior?
    - Did I follow existing codebase patterns?

    Fix any issues found during self-review before reporting.

    ## Report Format

    - **Status:** DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
    - What you implemented
    - What you tested and results
    - Files changed
    - Self-review findings (if any)
    - Concerns (if DONE_WITH_CONCERNS)

    DONE_WITH_CONCERNS = completed but have doubts about correctness.
    BLOCKED = cannot complete. NEEDS_CONTEXT = missing information.
    Never silently produce work you're unsure about.
```
````

- [ ] **Step 2: Verify file exists**

Run: `wc -l skills/implementing-tasks/implementer-subagent-prompt.md`
Expected: at least 40 lines

- [ ] **Step 3: Commit**

```bash
git add skills/implementing-tasks/implementer-subagent-prompt.md
git commit -m "feat: add implementer subagent prompt template"
```

---

### Task 2: Spec-compliance reviewer prompt template

**Files:**
- Create: `skills/implementing-tasks/spec-compliance-reviewer-prompt.md`

- [ ] **Step 1: Write the prompt template**

Create `skills/implementing-tasks/spec-compliance-reviewer-prompt.md`:

````markdown
# Spec-Compliance Reviewer Prompt Template

Use this template INSIDE the PAR wrapper when dispatching spec-compliance reviewers. This is Stage 1 of the two-stage review — it runs BEFORE code-quality review.

```
[REVIEWER INSTRUCTIONS — insert inside PAR wrapper from skills/shared/par-reviewer-wrapper.md]

You are reviewing whether an implementation matches its specification.

## What Was Requested

[FULL task description that was given to the implementer — paste it here]

## What the Implementer Claims They Built

[From the implementer's status report — what they say they did]

## CRITICAL: Do Not Trust the Report

The implementer may be incomplete, inaccurate, or optimistic. Verify
everything independently by reading the actual code.

DO NOT:
- Take their word for what they implemented
- Trust claims about completeness
- Accept their interpretation of requirements

DO:
- Read the actual code they wrote
- Compare implementation to requirements line by line
- Check for missing pieces
- Look for extra features not requested

## Check For

**Missing requirements:**
- Everything requested actually implemented?
- Requirements skipped or misunderstood?

**Extra/unneeded work:**
- Features built that weren't requested?
- Over-engineering or "nice to haves"?

**Misunderstandings:**
- Requirements interpreted differently than intended?
- Right feature, wrong approach?

## Report Format

For each finding, cite the specific file:line reference.

Overall: ✅ Spec compliant | ❌ Issues found: [list]
```
````

- [ ] **Step 2: Verify file exists**

Run: `wc -l skills/implementing-tasks/spec-compliance-reviewer-prompt.md`
Expected: at least 40 lines

- [ ] **Step 3: Commit**

```bash
git add skills/implementing-tasks/spec-compliance-reviewer-prompt.md
git commit -m "feat: add spec-compliance reviewer prompt template"
```

---

### Task 3: Code-quality reviewer prompt template

**Files:**
- Create: `skills/implementing-tasks/code-quality-reviewer-prompt.md`

- [ ] **Step 1: Write the prompt template**

Create `skills/implementing-tasks/code-quality-reviewer-prompt.md`:

````markdown
# Code-Quality Reviewer Prompt Template

Use this template INSIDE the PAR wrapper when dispatching code-quality reviewers. This is Stage 2 of the two-stage review — it runs AFTER spec-compliance review passes.

```
[REVIEWER INSTRUCTIONS — insert inside PAR wrapper from skills/shared/par-reviewer-wrapper.md]

You are reviewing code quality and architectural soundness.

## What Was Implemented

[From the implementer's report — summary of what was built]

## Your Job

Read the code that was changed and evaluate:

### Code Quality
- Is the code clean and maintainable?
- Are names clear and domain-appropriate (not implementation-descriptive)?
- Are there unnecessary abstractions or premature optimization?
- Is there dead code or unused imports?
- Are tests testing real behavior, not mock behavior?
- Does each file have one clear responsibility?

### Boxing-In Check

**Given the next 3 pending roadmap iterations:**

[Paste the next 3 iteration entries from roadmap.md here]

Does this implementation:
- Introduce hard coupling that would block any downstream iteration?
- Hardcode values that will need to be configurable later?
- Commit to interfaces that will need to change?
- Create structural decisions that would need to be undone?

If you can identify a specific downstream iteration that would be blocked
by a choice made in this code, that's a CRITICAL finding.

### Report Format

**Strengths:** [brief list]

**Issues:**
- Critical: [blocks correctness or downstream work — file:line refs]
- Serious: [significant quality problem — file:line refs]
- Minor: [style, naming — file:line refs]

**Boxing-In Assessment:** [CLEAR | RISK — with specific downstream iterations affected]

**Overall:** ✅ Approved | ❌ Changes needed
```
````

- [ ] **Step 2: Verify file exists**

Run: `wc -l skills/implementing-tasks/code-quality-reviewer-prompt.md`
Expected: at least 40 lines

- [ ] **Step 3: Commit**

```bash
git add skills/implementing-tasks/code-quality-reviewer-prompt.md
git commit -m "feat: add code-quality reviewer prompt with boxing-in check"
```

---

### Task 4: Rewrite implementing-tasks SKILL.md

**Files:**
- Modify: `skills/implementing-tasks/SKILL.md`

- [ ] **Step 1: Replace the SKILL.md with full SDD fork**

Replace the entire contents of `skills/implementing-tasks/SKILL.md` with:

```markdown
---
name: implementing-tasks
description: Use when executing a batch of TDD-sized tasks inside a running-an-iteration call — dispatches an implementer subagent per task following red-green-refactor discipline and returns per-task completion status.
---

# Implementing Tasks

## Overview

Takes an in-memory batch of TDD-sized tasks and executes each through: implementer subagent (TDD) → PAR spec-compliance review → fix loop → PAR code-quality review with boxing-in check → fix loop → mark complete. This is a fork of `superpowers:subagent-driven-development` with the plan-file reading phase stripped and the final end-of-plan reviewer removed.

## When to Use

Invoked by `running-an-iteration` with a list of tasks. Tasks are passed in memory, not via a file.

## Per-Task Cycle

For each task in the provided list:

### 1. Dispatch implementer

Using the template in `implementer-subagent-prompt.md`, dispatch a single implementer subagent with the full task description and context.

### 2. Handle implementer status

- **DONE:** proceed to spec-compliance review (step 3)
- **DONE_WITH_CONCERNS:** read the concerns. If about correctness/scope, address before review. If observations, note and proceed.
- **NEEDS_CONTEXT:** provide the missing context and re-dispatch
- **BLOCKED:** assess: context problem → re-dispatch with context; too hard → re-dispatch with more capable model; task too large → break into smaller pieces; plan wrong → escalate to caller

### 3. PAR spec-compliance review (Stage 1)

Following `skills/shared/parallel-adversarial-review.md`:

1. Build spec-compliance prompt using `spec-compliance-reviewer-prompt.md`
2. Wrap in PAR competitive framing from `skills/shared/par-reviewer-wrapper.md`
3. Dispatch TWO spec-compliance reviewers in parallel
4. Aggregate findings (PAR rules: union of findings, severity = take worst)
5. If ❌ issues found:
   - Send aggregated issues back to the implementer subagent (same subagent, via SendMessage)
   - Implementer fixes
   - Re-dispatch fresh PAR spec-compliance pair
   - Repeat until ✅ spec compliant
6. Only proceed to Stage 2 after Stage 1 is ✅

### 4. PAR code-quality review (Stage 2)

Following `skills/shared/parallel-adversarial-review.md`:

1. Build code-quality prompt using `code-quality-reviewer-prompt.md`
   - Include the next 3 pending roadmap iterations for the boxing-in check
2. Wrap in PAR competitive framing
3. Dispatch TWO code-quality reviewers in parallel
4. Aggregate findings
5. If ❌ changes needed:
   - Send aggregated issues back to the implementer
   - Implementer fixes
   - Re-dispatch fresh PAR code-quality pair
   - Repeat until ✅ approved

### 5. Mark task complete

Record the task as done. Move to the next task.

After all tasks complete, return a per-task result list to the caller.

## Model Selection

Use the least powerful model that can handle each role:

| Role | Signal → Model |
|---|---|
| Implementer (mechanical: 1-2 files, clear spec) | Cheap/fast model |
| Implementer (integration: multi-file, judgment) | Standard model |
| Spec-compliance reviewer | Standard model |
| Code-quality reviewer | Most capable model |

## Quick Reference

| Per task | Subagents dispatched |
|---|---|
| Implementer | 1 (sequential, TDD) |
| Spec-compliance review (PAR) | 2 in parallel |
| Code-quality review (PAR) | 2 in parallel |
| **Minimum per task** | **5** (before re-review loops) |

## Red Flags

- **Never** start code-quality review before spec compliance is ✅
- **Never** skip the re-review after fixes (reviewer found issues = implementer fixes = review again)
- **Never** dispatch multiple implementers in parallel (conflicts)
- **Never** accept "close enough" on spec compliance
- **Never** let implementer self-review replace the two-stage review

## References

- `implementer-subagent-prompt.md` — implementer dispatch template
- `spec-compliance-reviewer-prompt.md` — Stage 1 review template
- `code-quality-reviewer-prompt.md` — Stage 2 review template (includes boxing-in)
- `skills/shared/parallel-adversarial-review.md` — PAR methodology
- `skills/shared/par-reviewer-wrapper.md` — competitive framing wrapper
```

- [ ] **Step 2: Validate**

Run: `python3 scripts/validate_skill.py skills/implementing-tasks/SKILL.md`
Expected: OK (word count warning acceptable)

- [ ] **Step 3: Commit**

```bash
git add skills/implementing-tasks/SKILL.md
git commit -m "feat: update implementing-tasks with full two-stage PAR review cycle"
```

---

### Task 5: Update validation suite

**Files:**
- Modify: `scripts/run_validation_suite.sh`

- [ ] **Step 1: Add implementing-tasks prompt template checks**

Add the following section to `scripts/run_validation_suite.sh` BEFORE the final "All validation checks passed" line:

```bash
echo ""
echo "=== Verifying implementing-tasks prompt templates ==="
for tmpl in skills/implementing-tasks/*-prompt.md; do
    test -f "$tmpl" && echo "OK: $tmpl exists" || { echo "FAIL: $tmpl missing"; exit 1; }
done
```

- [ ] **Step 2: Run the full suite**

Run: `bash scripts/run_validation_suite.sh`
Expected: all checks pass

- [ ] **Step 3: Commit**

```bash
git add scripts/run_validation_suite.sh
git commit -m "chore: add implementing-tasks prompt template checks to validation suite"
```

---

## Plan Completion Checklist

- [ ] `skills/implementing-tasks/implementer-subagent-prompt.md` exists with TDD instructions + self-review + status reporting
- [ ] `skills/implementing-tasks/spec-compliance-reviewer-prompt.md` exists with "do not trust the report" framing
- [ ] `skills/implementing-tasks/code-quality-reviewer-prompt.md` exists with boxing-in check against next 3 iterations
- [ ] `skills/implementing-tasks/SKILL.md` describes full cycle: implementer → PAR spec review → fix → PAR quality review → fix → done
- [ ] SKILL.md has model selection guidance and red flags section
- [ ] All tests pass, validation suite passes

**Next plan:** Plan 6 — Autonomy + human interrupt protocol.
