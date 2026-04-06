# Quality Gates Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the three pre-implementation quality gates: (1) citation-check script that mechanically verifies every roadmap iteration cites valid story IDs, (2) pre-iteration scope review with PAR (citation + adversarial scope-creep check + boxing-in look-ahead), (3) two-tier audit scope (deep check on new work + light sweep on prior work). Update `scoping-the-simplest-core`, `running-an-iteration`, and `auditing-progress` skills.

**Architecture:** One new Python script (`scripts/check_citations.py`) for deterministic citation verification, plus prompt templates for scope reviewers. Three SKILL.md updates adding gate logic and PAR references. The citation checker is the only testable code; scope review and boxing-in check are instructional (LLM judgment, guided by prompts).

**Tech Stack:** Python 3 stdlib (citation checker), Markdown (skills, prompts)

---

## File Structure

```
scripts/
  check_citations.py                                    # NEW: verify roadmap story citations exist in index
tests/
  test_check_citations.py                               # NEW: unit tests for citation checker
skills/
  running-an-iteration/
    SKILL.md                                            # MODIFY: add pre-iteration scope review
    scope-reviewer-prompt.md                            # NEW: prompt for scope review subagents
  scoping-the-simplest-core/
    SKILL.md                                            # MODIFY: add scope review during roadmap creation
  auditing-progress/
    SKILL.md                                            # MODIFY: add two-tier audit scope
```

---

### Task 1: Citation checker script

**Files:**
- Create: `scripts/check_citations.py`
- Create: `tests/test_check_citations.py`

The citation checker reads a roadmap.md and requirements-index.md and verifies every STORY-NNNN cited in the roadmap exists in the requirements index. This is a deterministic check that can be run before any LLM-driven review.

- [ ] **Step 1: Write failing tests**

Create `tests/test_check_citations.py`:

```python
"""Unit tests for scripts/check_citations.py."""
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "scripts" / "check_citations.py"
FIXTURES = Path(__file__).parent / "fixtures"


class TestCheckCitations(unittest.TestCase):
    def test_script_exists(self):
        self.assertTrue(SCRIPT.exists())

    def test_valid_fixtures_pass(self):
        """The example roadmap cites STORY-0001 which exists in the example index."""
        result = subprocess.run(
            ["python3", str(SCRIPT),
             str(FIXTURES / "roadmap.example.md"),
             str(FIXTURES / "requirements-index.example.md")],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)

    def test_missing_story_is_flagged(self):
        """A roadmap citing a story that doesn't exist should fail."""
        import os
        roadmap = "# Roadmap\n\n## Walking skeleton (ITER-0000)\n\n**Intent:** test\n**Stories committed:**\n- STORY-9999 (EPIC-001)\n**Status:** pending\n\n## Iteration list\n"
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
            f.write(roadmap)
            tmp_roadmap = f.name
        try:
            result = subprocess.run(
                ["python3", str(SCRIPT), tmp_roadmap,
                 str(FIXTURES / "requirements-index.example.md")],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("STORY-9999", result.stderr)
        finally:
            os.unlink(tmp_roadmap)

    def test_missing_file_returns_error(self):
        result = subprocess.run(
            ["python3", str(SCRIPT), "/tmp/no-such-file.md", "/tmp/no-such-index.md"],
            capture_output=True, text=True,
        )
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest tests.test_check_citations -v`
Expected: FAIL

- [ ] **Step 3: Implement the citation checker**

Create `scripts/check_citations.py`:

```python
#!/usr/bin/env python3
"""Verify every story cited in a roadmap exists in the requirements index.

Usage: check_citations.py <roadmap.md> <requirements-index.md>

Exit code: 0 if all citations valid, 1 if any missing, 2 on usage error.
"""
import re
import sys
from pathlib import Path


def extract_cited_stories(roadmap_content: str) -> set[str]:
    """Extract all STORY-NNNN references from roadmap content."""
    return set(re.findall(r"STORY-\d+", roadmap_content))


def extract_defined_stories(index_content: str) -> set[str]:
    """Extract all ## STORY-NNNN headers from requirements index."""
    return set(re.findall(r"^## (STORY-\d+)", index_content, re.MULTILINE))


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: check_citations.py <roadmap.md> <requirements-index.md>",
              file=sys.stderr)
        return 2

    roadmap_path = Path(sys.argv[1])
    index_path = Path(sys.argv[2])

    for p in (roadmap_path, index_path):
        if not p.exists():
            print(f"error: file not found: {p}", file=sys.stderr)
            return 2

    cited = extract_cited_stories(roadmap_path.read_text())
    defined = extract_defined_stories(index_path.read_text())

    missing = cited - defined
    if missing:
        for story_id in sorted(missing):
            print(f"error: {story_id} cited in roadmap but not found in requirements index",
                  file=sys.stderr)
        return 1

    print(f"OK: all {len(cited)} cited stories exist in requirements index")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

Make executable: `chmod +x scripts/check_citations.py`

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest tests.test_check_citations -v`
Expected: all 4 tests pass

Run: `python3 -m unittest discover tests/ -v`
Expected: all 34 tests pass (30 prior + 4 new)

- [ ] **Step 5: Commit**

```bash
git add scripts/check_citations.py tests/test_check_citations.py
git commit -m "feat: add citation checker for roadmap → requirements-index verification"
```

---

### Task 2: Scope reviewer prompt template

**Files:**
- Create: `skills/running-an-iteration/scope-reviewer-prompt.md`

- [ ] **Step 1: Write the prompt template**

Create `skills/running-an-iteration/scope-reviewer-prompt.md`:

````markdown
# Scope Reviewer Prompt Template

Use this template inside the PAR wrapper when dispatching scope review subagents before an iteration starts.

```
[REVIEWER INSTRUCTIONS — insert inside PAR wrapper from skills/shared/par-reviewer-wrapper.md]

You are reviewing the scope of an upcoming iteration BEFORE any code is written.

## Iteration Being Reviewed

[Paste the iteration entry from roadmap.md — stories committed, rationale]

## Stories in Scope

[For each committed story, paste the full story card from requirements-index.md]

## Next 3 Pending Iterations

[Paste the next 3 iteration entries from roadmap.md for look-ahead]

## Your Three Checks

### 1. Citation Integrity

For every story committed to this iteration:
- Does it cite a valid STORY-NNNN that exists in requirements-index.md?
- Does each story's acceptance criteria match what the source spec says?
(Note: the mechanical citation check via check_citations.py has already run.
Your job is the SEMANTIC check — do the stories actually mean what the spec says?)

### 2. Scope Creep

- Is this iteration trying to do too much for a single sprint?
- Could any story be deferred to a later iteration without breaking the current one?
- Are there stories here that don't need to be bundled together?

### 3. Boxing-In Look-Ahead

Given this iteration's planned design approach:
- Would iterations N+1, N+2, or N+3 be BLOCKED by architectural choices made here?
- Does this iteration introduce hard coupling, premature abstraction, or structural commitments that would need to be undone later?
- Could the same functionality be achieved with fewer commitments?

## Report Format

For each check:
- **Citation Integrity:** [PASS | issues found]
- **Scope Creep:** [PASS | recommendations to defer/split]
- **Boxing-In:** [PASS | risks identified with specific downstream iterations affected]

Overall: [APPROVE | REVISE — with specific changes needed]
```
````

- [ ] **Step 2: Verify file exists**

Run: `wc -l skills/running-an-iteration/scope-reviewer-prompt.md`
Expected: at least 40 lines

- [ ] **Step 3: Commit**

```bash
git add skills/running-an-iteration/scope-reviewer-prompt.md
git commit -m "feat: add scope reviewer prompt template with citation + scope-creep + boxing-in checks"
```

---

### Task 3: Update running-an-iteration SKILL.md

**Files:**
- Modify: `skills/running-an-iteration/SKILL.md`

- [ ] **Step 1: Replace the SKILL.md with quality-gate-enabled version**

Replace the entire contents of `skills/running-an-iteration/SKILL.md` with:

```markdown
---
name: running-an-iteration
description: Use when executing the next pending iteration from an iterative-development roadmap — picks the iteration, decomposes it into tasks, dispatches implementing-tasks, and updates the roadmap and iteration log.
---

# Running an Iteration

## Overview

Drives one iteration: picks the next pending, runs a pre-iteration scope review via PAR, decomposes into TDD tasks, dispatches `implementing-tasks`, and updates the roadmap and iteration log.

## When to Use

Invoked by `iterative-development` inside the main loop. Each invocation runs exactly one iteration. After return, the orchestrator invokes `auditing-progress`.

## Iteration Process

### 1. Pick next iteration

Read `docs/superpowers/iterations/roadmap.md`, find the first iteration with status `pending`.

### 2. Load scope context

Read `docs/superpowers/iterations/requirements-index.md`, load the full story cards for each committed story ID. Also load the next 3 pending iterations from the roadmap for look-ahead.

### 3. Mechanical citation check

Run: `python3 scripts/check_citations.py docs/superpowers/iterations/roadmap.md docs/superpowers/iterations/requirements-index.md`

If citations fail, stop and fix the roadmap before proceeding.

### 4. Pre-iteration scope review (PAR)

Following `skills/shared/parallel-adversarial-review.md`:

1. Build the scope reviewer prompt using `scope-reviewer-prompt.md`
2. Wrap in PAR competitive framing from `skills/shared/par-reviewer-wrapper.md`
3. Dispatch TWO scope reviewers in parallel (Agent tool, two calls in one message)
4. Aggregate findings: same issue from both = high confidence, unique = still actionable, severity disagreement = take worst
5. If REVISE recommended: adjust iteration scope and re-review. Loop until APPROVE.

### 5. Decompose into tasks

Break the iteration scope into TDD-sized tasks. Each task = failing test → implementation → passing test → commit. Iteration granularity is judgment-based, not defaulted.

### 6. Dispatch implementing-tasks

Pass the task list and iteration context to `implementing-tasks`. Wait for completion.

### 7. Wrap up

- Verify all iteration stories' ACs pass (sanity check before audit)
- Mark stories `done:ITER-NNNN` in `requirements-index.md`
- Update iteration status in `roadmap.md` to `done`
- Append entry to `docs/superpowers/iterations/iteration-log.md`
- Validate: `python3 scripts/validate_artifact.py --type iteration-log docs/superpowers/iterations/iteration-log.md`
- Return control to orchestrator (do NOT invoke `auditing-progress` — that's the orchestrator's job)

## Quick Reference

| Step | Tool/Skill | Purpose |
|---|---|---|
| Citation check | `scripts/check_citations.py` | Mechanical: cited stories exist |
| Scope review | PAR + `scope-reviewer-prompt.md` | Semantic: scope creep, boxing-in |
| Task execution | `implementing-tasks` | TDD implementation |
| Wrap up | `scripts/validate_artifact.py` | Artifact validation |

## References

- `skills/shared/parallel-adversarial-review.md` — PAR methodology
- `scope-reviewer-prompt.md` — scope reviewer prompt template
- `scripts/check_citations.py` — mechanical citation check
```

- [ ] **Step 2: Validate**

Run: `python3 scripts/validate_skill.py skills/running-an-iteration/SKILL.md`
Expected: OK (word count warning acceptable)

- [ ] **Step 3: Commit**

```bash
git add skills/running-an-iteration/SKILL.md
git commit -m "feat: update running-an-iteration with pre-iteration scope review and PAR"
```

---

### Task 4: Update scoping-the-simplest-core SKILL.md

**Files:**
- Modify: `skills/scoping-the-simplest-core/SKILL.md`

- [ ] **Step 1: Replace the SKILL.md**

Replace the entire contents of `skills/scoping-the-simplest-core/SKILL.md` with:

```markdown
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
```

- [ ] **Step 2: Validate**

Run: `python3 scripts/validate_skill.py skills/scoping-the-simplest-core/SKILL.md`
Expected: OK

- [ ] **Step 3: Commit**

```bash
git add skills/scoping-the-simplest-core/SKILL.md
git commit -m "feat: update scoping-the-simplest-core with citation check and PAR scope review"
```

---

### Task 5: Update auditing-progress with two-tier scope

**Files:**
- Modify: `skills/auditing-progress/SKILL.md`

- [ ] **Step 1: Add two-tier audit scope to the SKILL.md**

In `skills/auditing-progress/SKILL.md`, replace the "Identify stories to audit" section (step 1) with a two-tier partitioning:

Find the section that starts with `### 1. Identify stories to audit` and replace it with:

```markdown
### 1. Partition the audit into two tiers

Read `docs/superpowers/iterations/requirements-index.md`:

- **Deep tier:** stories marked `done:ITER-<current>` — the ones this iteration just delivered. Audit every AC thoroughly.
- **Sweep tier:** all other stories previously marked `done:ITER-<earlier>`. Light sanity check — run test suites, spot-check ACs, look for regressions. Not a full re-verification.
```

Then update the "Dispatch paired auditor subagents" section's step 1 to include both tiers:

Replace the line that says "Build the auditor prompt using the template in `auditor-subagent-prompt.md`" with:

```markdown
1. Build the auditor prompt using `auditor-subagent-prompt.md`. Include BOTH tiers:
   - Deep tier: paste full story cards with all ACs for just-done stories
   - Sweep tier: paste story IDs and test commands for previously-done stories (not full cards)
```

- [ ] **Step 2: Validate**

Run: `python3 scripts/validate_skill.py skills/auditing-progress/SKILL.md`
Expected: OK

- [ ] **Step 3: Commit**

```bash
git add skills/auditing-progress/SKILL.md
git commit -m "feat: add two-tier audit scope (deep + sweep) to auditing-progress"
```

---

### Task 6: Update validation suite

**Files:**
- Modify: `scripts/run_validation_suite.sh`

- [ ] **Step 1: Add citation checker to the suite**

Add the following section to `scripts/run_validation_suite.sh` BEFORE the PAR verification section:

```bash
echo ""
echo "=== Verifying citation checker ==="
python3 scripts/check_citations.py tests/fixtures/roadmap.example.md tests/fixtures/requirements-index.example.md
test -f skills/running-an-iteration/scope-reviewer-prompt.md && echo "OK: scope-reviewer-prompt.md exists" || { echo "FAIL: scope-reviewer-prompt.md missing"; exit 1; }
```

- [ ] **Step 2: Run the full suite**

Run: `bash scripts/run_validation_suite.sh`
Expected: all checks pass

- [ ] **Step 3: Commit**

```bash
git add scripts/run_validation_suite.sh
git commit -m "chore: add citation checker and scope reviewer prompt to validation suite"
```

---

## Plan Completion Checklist

- [ ] `scripts/check_citations.py` exists, is executable, and passes its 4 unit tests
- [ ] `skills/running-an-iteration/scope-reviewer-prompt.md` exists with 3 scope checks (citation, scope-creep, boxing-in)
- [ ] `running-an-iteration/SKILL.md` updated with pre-iteration scope review via PAR
- [ ] `scoping-the-simplest-core/SKILL.md` updated with citation check and PAR scope review
- [ ] `auditing-progress/SKILL.md` updated with two-tier audit scope (deep + sweep)
- [ ] All 34+ tests pass, `bash scripts/run_validation_suite.sh` passes

**Next plan:** Plan 5 — implementing-tasks (full SDD fork with two-stage review).
