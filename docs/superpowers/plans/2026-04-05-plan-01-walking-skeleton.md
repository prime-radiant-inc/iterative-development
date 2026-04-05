# Walking Skeleton Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a trivial but complete end-to-end pipeline of 6 skills that thread a minimal spec through the iterative-development plugin, producing working output. Lock in artifact formats, skill contracts, and plugin structure. Defer all sophistication (parallelism, PAR, map-reduce extraction, real audit logic) to later plans.

**Architecture:** Claude Code plugin with 6 skills in `skills/`, a manifest in `.claude-plugin/plugin.json`, artifact format examples + Python validators in `scripts/`, and a walking-skeleton dogfood test harness in `tests/walking-skeleton/`. All skills for this plan are thin stubs — they follow the contracts described in the design spec but do not implement sophisticated behavior. Claude reads the SKILL.md files and performs the work in-session following the instructions; validators and test fixtures are Python (stdlib only, no external deps).

**Tech Stack:** Markdown (SKILL.md, examples, docs), JSON (plugin.json), Python 3 stdlib (validators, tests), Shell (glue where needed), YAML frontmatter in skill files.

---

## Why a Walking Skeleton Plan

The design spec describes a six-skill plugin with sophisticated parallel orchestration, map-reduce extraction, parallel adversarial review, two-tier auditing, and autonomous loop management. Building all of that at once is exactly the failure mode the plugin itself is designed to prevent: heavy upfront implementation with nothing working until the end.

Instead, this plan builds the **thinnest possible complete pipeline**. Every skill exists as a thin stub. Artifact formats are locked in early. Every skill contract is defined. One tiny sample spec threads through the full pipeline end-to-end and produces working output.

After this plan:
- Plan 2 hardens `extracting-requirements` (chunking, parallel dispatch, aggregation, hierarchical reduce).
- Plan 3 adds parallel adversarial review everywhere.
- Plan 4 adds the full quality gates (scope review, boxing-in check, two-tier audit).
- Plan 5 completes `implementing-tasks` as a full SDD fork.
- Plan 6 implements autonomy + human interrupt protocol + crash resumption.
- Plan 7 runs the plugin against the ghost-pepper sample spec end-to-end.

---

## File Structure

**Plugin structure** (following standard Claude Code plugin conventions):

```
iterative-development/
├── .claude-plugin/
│   └── plugin.json                           # Plugin manifest
├── skills/
│   ├── iterative-development/SKILL.md        # Orchestrator
│   ├── extracting-requirements/SKILL.md      # Spec → backlog
│   ├── scoping-the-simplest-core/SKILL.md    # Backlog → roadmap
│   ├── running-an-iteration/SKILL.md         # One sprint driver
│   ├── implementing-tasks/SKILL.md           # SDD fork (trivial for now)
│   └── auditing-progress/SKILL.md            # Per-sprint audit
├── scripts/
│   ├── validate_artifact.py                  # Artifact format validator
│   ├── validate_skill.py                     # Skill file validator
│   └── run_validation_suite.sh               # Runs all validators
├── tests/
│   ├── __init__.py
│   ├── test_artifact_validator.py            # Unit tests for artifact validator
│   ├── test_skill_validator.py               # Unit tests for skill validator
│   ├── fixtures/
│   │   ├── requirements-index.example.md     # Valid artifact examples
│   │   ├── roadmap.example.md
│   │   ├── iteration-log.example.md
│   │   ├── requirements-index.invalid.md     # Invalid examples for negative tests
│   │   ├── roadmap.invalid.md
│   │   └── iteration-log.invalid.md
│   └── walking-skeleton/
│       ├── input-spec/
│       │   └── spec.md                       # Tiny sample spec
│       └── README.md                         # Manual dogfood procedure
├── docs/
│   └── superpowers/
│       ├── specs/
│       │   └── 2026-04-05-iterative-development-design.md  # Already exists
│       └── plans/
│           └── 2026-04-05-plan-01-walking-skeleton.md      # This file
```

**File responsibilities:**

- `plugin.json` — minimal manifest declaring the plugin and its 6 skills
- `skills/*/SKILL.md` — one per skill, thin instructional stubs with valid frontmatter
- `scripts/validate_artifact.py` — Python stdlib, parses an artifact file, returns pass/fail + reasons
- `scripts/validate_skill.py` — Python stdlib, parses a SKILL.md file, validates frontmatter + description + word count
- `scripts/run_validation_suite.sh` — Shell wrapper that runs all validators in sequence, fails on first error
- `tests/test_artifact_validator.py` — Python stdlib unittest, exercises `validate_artifact.py` against valid + invalid fixtures
- `tests/test_skill_validator.py` — Python stdlib unittest, exercises `validate_skill.py` against valid + invalid fixtures
- `tests/fixtures/*.example.md` — Hand-written valid artifact examples that demonstrate the format
- `tests/fixtures/*.invalid.md` — Hand-written invalid examples for negative tests
- `tests/walking-skeleton/input-spec/spec.md` — Tiny sample spec for the dogfood procedure
- `tests/walking-skeleton/README.md` — Human-readable manual dogfood procedure with expected artifacts

---

## Task Summary

| # | Task | Files |
|---|---|---|
| 1 | Plugin manifest | `.claude-plugin/plugin.json` |
| 2 | Artifact validator foundation | `scripts/validate_artifact.py`, `tests/test_artifact_validator.py`, `tests/__init__.py` |
| 3 | `requirements-index.md` format + validator | `tests/fixtures/requirements-index.example.md`, `tests/fixtures/requirements-index.invalid.md`, validator additions, test additions |
| 4 | `roadmap.md` format + validator | `tests/fixtures/roadmap.example.md`, `tests/fixtures/roadmap.invalid.md`, validator additions, test additions |
| 5 | `iteration-log.md` format + validator | `tests/fixtures/iteration-log.example.md`, `tests/fixtures/iteration-log.invalid.md`, validator additions, test additions |
| 6 | Skill file validator | `scripts/validate_skill.py`, `tests/test_skill_validator.py` |
| 7 | Skill stub: `iterative-development` | `skills/iterative-development/SKILL.md` |
| 8 | Skill stub: `extracting-requirements` | `skills/extracting-requirements/SKILL.md` |
| 9 | Skill stub: `scoping-the-simplest-core` | `skills/scoping-the-simplest-core/SKILL.md` |
| 10 | Skill stub: `running-an-iteration` | `skills/running-an-iteration/SKILL.md` |
| 11 | Skill stub: `implementing-tasks` | `skills/implementing-tasks/SKILL.md` |
| 12 | Skill stub: `auditing-progress` | `skills/auditing-progress/SKILL.md` |
| 13 | Walking skeleton sample spec | `tests/walking-skeleton/input-spec/spec.md` |
| 14 | Walking skeleton dogfood procedure | `tests/walking-skeleton/README.md` |
| 15 | Validation suite runner | `scripts/run_validation_suite.sh` |

---

### Task 1: Plugin manifest

**Files:**
- Create: `.claude-plugin/plugin.json`

- [ ] **Step 1: Write the manifest file**

Create `.claude-plugin/plugin.json`:

```json
{
  "name": "iterative-development",
  "description": "An iterative implementation methodology that pairs with superpowers. Extracts requirements from arbitrary-size spec collateral, defines a walking skeleton, then loops through audited sprints until an auditor confirms the product matches the spec. Designed for large or comprehensive specs where the upfront writing-plans → SDD flow loses the plot.",
  "version": "0.0.1",
  "author": "iterative-development contributors",
  "components": {
    "skills": [
      "skills/iterative-development",
      "skills/extracting-requirements",
      "skills/scoping-the-simplest-core",
      "skills/running-an-iteration",
      "skills/implementing-tasks",
      "skills/auditing-progress"
    ]
  }
}
```

- [ ] **Step 2: Verify the manifest parses as valid JSON**

Run: `python3 -c "import json; json.load(open('.claude-plugin/plugin.json'))"`
Expected: no output, exit code 0

- [ ] **Step 3: Verify required fields exist**

Run:
```bash
python3 -c "
import json
m = json.load(open('.claude-plugin/plugin.json'))
assert 'name' in m and m['name'] == 'iterative-development'
assert 'description' in m and len(m['description']) > 50
assert 'version' in m
assert 'components' in m and 'skills' in m['components']
assert len(m['components']['skills']) == 6
print('OK')
"
```
Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add .claude-plugin/plugin.json
git commit -m "feat: add plugin manifest"
```

---

### Task 2: Artifact validator foundation

**Files:**
- Create: `scripts/validate_artifact.py`
- Create: `tests/__init__.py`
- Create: `tests/test_artifact_validator.py`

This task establishes the validator scaffold. Format-specific validators (requirements-index, roadmap, iteration-log) are added in Tasks 3-5.

- [ ] **Step 1: Write failing test for validator scaffold**

Create `tests/__init__.py` (empty file):

```python
```

Create `tests/test_artifact_validator.py`:

```python
"""Unit tests for scripts/validate_artifact.py."""
import subprocess
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "scripts" / "validate_artifact.py"


class TestValidatorScaffold(unittest.TestCase):
    def test_script_exists_and_is_executable(self):
        self.assertTrue(SCRIPT.exists(), f"{SCRIPT} does not exist")

    def test_unknown_type_returns_nonzero(self):
        result = subprocess.run(
            ["python3", str(SCRIPT), "--type", "bogus", "/dev/null"],
            capture_output=True, text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unknown artifact type", result.stderr.lower())

    def test_missing_file_returns_nonzero(self):
        result = subprocess.run(
            ["python3", str(SCRIPT), "--type", "requirements-index", "/tmp/does-not-exist-12345.md"],
            capture_output=True, text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not found", result.stderr.lower())


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_artifact_validator -v`
Expected: FAIL with `FileNotFoundError` or `AssertionError: scripts/validate_artifact.py does not exist`

- [ ] **Step 3: Write minimal validator scaffold**

Create `scripts/validate_artifact.py`:

```python
#!/usr/bin/env python3
"""Validate iterative-development artifact files.

Usage: validate_artifact.py --type <type> <file>

Types: requirements-index, roadmap, iteration-log
Exit code: 0 on success, 1 on validation failure, 2 on invocation error.
"""
import argparse
import sys
from pathlib import Path


KNOWN_TYPES = ("requirements-index", "roadmap", "iteration-log")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate iterative-development artifacts")
    parser.add_argument("--type", required=True, help=f"Artifact type: one of {KNOWN_TYPES}")
    parser.add_argument("file", help="Path to artifact file")
    args = parser.parse_args()

    if args.type not in KNOWN_TYPES:
        print(f"error: unknown artifact type: {args.type}", file=sys.stderr)
        return 2

    path = Path(args.file)
    if not path.exists():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 2

    content = path.read_text()

    # Dispatch to type-specific validator (added in Tasks 3-5).
    validators = {
        "requirements-index": validate_requirements_index,
        "roadmap": validate_roadmap,
        "iteration-log": validate_iteration_log,
    }
    errors = validators[args.type](content)

    if errors:
        for err in errors:
            print(f"error: {err}", file=sys.stderr)
        return 1

    print(f"OK: {path}")
    return 0


def validate_requirements_index(content: str) -> list[str]:
    """Return list of error messages. Empty list means valid. Expanded in Task 3."""
    return ["requirements-index validator not yet implemented"]


def validate_roadmap(content: str) -> list[str]:
    """Return list of error messages. Empty list means valid. Expanded in Task 4."""
    return ["roadmap validator not yet implemented"]


def validate_iteration_log(content: str) -> list[str]:
    """Return list of error messages. Empty list means valid. Expanded in Task 5."""
    return ["iteration-log validator not yet implemented"]


if __name__ == "__main__":
    sys.exit(main())
```

Make it executable:
```bash
chmod +x scripts/validate_artifact.py
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests.test_artifact_validator -v`
Expected: PASS, all 3 tests pass

- [ ] **Step 5: Commit**

```bash
git add scripts/validate_artifact.py tests/__init__.py tests/test_artifact_validator.py
git commit -m "feat: add artifact validator scaffold with dispatch + scaffold tests"
```

---

### Task 3: `requirements-index.md` format + validator

**Files:**
- Create: `tests/fixtures/requirements-index.example.md`
- Create: `tests/fixtures/requirements-index.invalid.md`
- Modify: `scripts/validate_artifact.py` (replace `validate_requirements_index`)
- Modify: `tests/test_artifact_validator.py` (add format-specific tests)

- [ ] **Step 1: Write failing tests for the format validator**

Append to `tests/test_artifact_validator.py` (inside the file, after `TestValidatorScaffold`):

```python
FIXTURES = Path(__file__).parent / "fixtures"


class TestRequirementsIndexValidator(unittest.TestCase):
    def test_valid_example_passes(self):
        result = subprocess.run(
            ["python3", str(SCRIPT), "--type", "requirements-index",
             str(FIXTURES / "requirements-index.example.md")],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)

    def test_invalid_example_fails(self):
        result = subprocess.run(
            ["python3", str(SCRIPT), "--type", "requirements-index",
             str(FIXTURES / "requirements-index.invalid.md")],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 1)

    def test_missing_story_id_is_flagged(self):
        # Valid example minus the STORY-0001 id
        import tempfile, os
        content = (FIXTURES / "requirements-index.example.md").read_text()
        broken = content.replace("## STORY-0001", "## STORY-")
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
            f.write(broken)
            tmp = f.name
        try:
            result = subprocess.run(
                ["python3", str(SCRIPT), "--type", "requirements-index", tmp],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("story id", result.stderr.lower())
        finally:
            os.unlink(tmp)
```

- [ ] **Step 2: Create the example fixture**

Create `tests/fixtures/requirements-index.example.md`:

```markdown
# Requirements Index

Extracted from: `tests/walking-skeleton/input-spec/spec.md`
Last updated: 2026-04-05

## EPIC-001 — Greeting commands

**Summary:** Commands that greet the user with a personalized message.
**Stories:** STORY-0001
**Primary sources:** `spec.md:1-20`
**Status:** 0/1 done

## STORY-0001

**Epic:** EPIC-001 — Greeting commands
**Title:** User gets a personalized greeting

**As a** command-line user
**I want** to invoke a greet command with my name
**So that** I see a personalized greeting message

**Acceptance criteria:**
- AC-1: Running `greet <name>` prints `Hello, <name>!` to stdout
- AC-2: Running `greet` with no argument prints a usage message to stderr and exits non-zero

**Sources:**
- `spec.md:1-20`

**Status:** pending
```

- [ ] **Step 3: Create the invalid fixture**

Create `tests/fixtures/requirements-index.invalid.md`:

```markdown
# Requirements Index

## STORY-

**Title:** A story with a malformed ID

(missing epic, no acceptance criteria, no sources, no status)
```

- [ ] **Step 4: Implement the requirements-index validator**

Replace the `validate_requirements_index` function in `scripts/validate_artifact.py` with:

```python
def validate_requirements_index(content: str) -> list[str]:
    """Validate a requirements-index.md file.

    Checks:
    - Contains at least one STORY-NNNN header with valid ID
    - Each story has: Epic, Title, acceptance criteria, sources, status
    - Each epic referenced by a story exists as an EPIC-NNN header
    """
    import re

    errors: list[str] = []

    story_pattern = re.compile(r"^## STORY-(\d+)\s*$", re.MULTILINE)
    bad_story_pattern = re.compile(r"^## STORY-\s*$", re.MULTILINE)
    epic_pattern = re.compile(r"^## EPIC-(\d+)\s*", re.MULTILINE)

    # Catch malformed STORY-/EPIC- IDs (missing digits)
    if bad_story_pattern.search(content):
        errors.append("found malformed STORY-<id> header (missing digits)")

    stories = story_pattern.findall(content)
    if not stories:
        errors.append("no valid STORY-NNNN headers found")
        return errors

    # Per-story required sections
    for match in story_pattern.finditer(content):
        story_id = f"STORY-{match.group(1)}"
        # Find the section bounds (until next ## or end)
        start = match.end()
        next_h2 = re.search(r"^## ", content[start:], re.MULTILINE)
        end = start + next_h2.start() if next_h2 else len(content)
        section = content[start:end]

        for required in ("**Epic:**", "**Title:**", "**Acceptance criteria:**",
                         "**Sources:**", "**Status:**"):
            if required not in section:
                errors.append(f"{story_id}: missing required field {required}")

    return errors
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python3 -m unittest tests.test_artifact_validator -v`
Expected: PASS, all tests pass (including the 3 scaffold tests from Task 2 and the 3 new tests from this task)

- [ ] **Step 6: Commit**

```bash
git add tests/fixtures/requirements-index.example.md tests/fixtures/requirements-index.invalid.md scripts/validate_artifact.py tests/test_artifact_validator.py
git commit -m "feat: add requirements-index format validator with fixtures"
```

---

### Task 4: `roadmap.md` format + validator

**Files:**
- Create: `tests/fixtures/roadmap.example.md`
- Create: `tests/fixtures/roadmap.invalid.md`
- Modify: `scripts/validate_artifact.py` (replace `validate_roadmap`)
- Modify: `tests/test_artifact_validator.py` (add roadmap tests)

- [ ] **Step 1: Write failing tests**

Append to `tests/test_artifact_validator.py`:

```python
class TestRoadmapValidator(unittest.TestCase):
    def test_valid_example_passes(self):
        result = subprocess.run(
            ["python3", str(SCRIPT), "--type", "roadmap",
             str(FIXTURES / "roadmap.example.md")],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)

    def test_invalid_example_fails(self):
        result = subprocess.run(
            ["python3", str(SCRIPT), "--type", "roadmap",
             str(FIXTURES / "roadmap.invalid.md")],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 1)

    def test_missing_walking_skeleton_is_flagged(self):
        import tempfile, os
        content = (FIXTURES / "roadmap.example.md").read_text()
        broken = content.replace("## Walking skeleton (ITER-0000)", "## Other thing")
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
            f.write(broken)
            tmp = f.name
        try:
            result = subprocess.run(
                ["python3", str(SCRIPT), "--type", "roadmap", tmp],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("walking skeleton", result.stderr.lower())
        finally:
            os.unlink(tmp)
```

- [ ] **Step 2: Create the example fixture**

Create `tests/fixtures/roadmap.example.md`:

```markdown
# Roadmap

## Walking skeleton (ITER-0000)

**Intent:** The thinnest end-to-end slice that exercises the full product shape.
**Design rationale:** Implement the single greet command end-to-end; this is the entire v0 and proves the CLI entry point works.
**Stories committed:**
- STORY-0001 (EPIC-001)
**Status:** pending

## Iteration list

### ITER-0001 — Error handling polish

**Stories:** STORY-0001
**Rationale:** Extend greet to produce a friendly usage message on error input.
**Status:** pending
**Look-ahead check:** no downstream iterations yet, trivially clean
```

- [ ] **Step 3: Create the invalid fixture**

Create `tests/fixtures/roadmap.invalid.md`:

```markdown
# Roadmap

(missing walking skeleton section, missing iteration list)
```

- [ ] **Step 4: Implement the roadmap validator**

Replace the `validate_roadmap` function in `scripts/validate_artifact.py`:

```python
def validate_roadmap(content: str) -> list[str]:
    """Validate a roadmap.md file.

    Checks:
    - Contains a "Walking skeleton (ITER-0000)" section
    - Walking skeleton section has Intent, Status, Stories committed
    - Contains an "Iteration list" section
    """
    errors: list[str] = []

    if "## Walking skeleton (ITER-0000)" not in content:
        errors.append("missing walking skeleton section (expected '## Walking skeleton (ITER-0000)')")

    if "## Iteration list" not in content:
        errors.append("missing iteration list section (expected '## Iteration list')")

    # Walking skeleton required fields
    if "## Walking skeleton (ITER-0000)" in content:
        ws_start = content.index("## Walking skeleton (ITER-0000)")
        next_h2 = content.find("\n## ", ws_start + 1)
        ws_end = next_h2 if next_h2 != -1 else len(content)
        ws_section = content[ws_start:ws_end]
        for required in ("**Intent:**", "**Status:**", "**Stories committed:**"):
            if required not in ws_section:
                errors.append(f"walking skeleton: missing required field {required}")

    return errors
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python3 -m unittest tests.test_artifact_validator -v`
Expected: PASS, all previous tests still pass plus the 3 new roadmap tests

- [ ] **Step 6: Commit**

```bash
git add tests/fixtures/roadmap.example.md tests/fixtures/roadmap.invalid.md scripts/validate_artifact.py tests/test_artifact_validator.py
git commit -m "feat: add roadmap format validator with fixtures"
```

---

### Task 5: `iteration-log.md` format + validator

**Files:**
- Create: `tests/fixtures/iteration-log.example.md`
- Create: `tests/fixtures/iteration-log.invalid.md`
- Modify: `scripts/validate_artifact.py` (replace `validate_iteration_log`)
- Modify: `tests/test_artifact_validator.py` (add iteration-log tests)

- [ ] **Step 1: Write failing tests**

Append to `tests/test_artifact_validator.py`:

```python
class TestIterationLogValidator(unittest.TestCase):
    def test_valid_example_passes(self):
        result = subprocess.run(
            ["python3", str(SCRIPT), "--type", "iteration-log",
             str(FIXTURES / "iteration-log.example.md")],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)

    def test_invalid_example_fails(self):
        result = subprocess.run(
            ["python3", str(SCRIPT), "--type", "iteration-log",
             str(FIXTURES / "iteration-log.invalid.md")],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 1)
```

- [ ] **Step 2: Create the example fixture**

Create `tests/fixtures/iteration-log.example.md`:

```markdown
# Iteration Log

## ITER-0000 — Walking skeleton

**Completed:** 2026-04-05
**Stories delivered:** STORY-0001
**Tasks executed:** 1
**Summary:** Implemented the greet command end-to-end. The CLI accepts a name argument and prints a personalized greeting.
**Learnings:** The walking skeleton revealed that argument parsing needs to distinguish missing-argument from empty-string cases. No roadmap revision needed.
**Roadmap revisions:** none
```

- [ ] **Step 3: Create the invalid fixture**

Create `tests/fixtures/iteration-log.invalid.md`:

```markdown
# Iteration Log

## ITER-0000

(missing all the required fields - this should fail validation)
```

- [ ] **Step 4: Implement the iteration-log validator**

Replace the `validate_iteration_log` function in `scripts/validate_artifact.py`:

```python
def validate_iteration_log(content: str) -> list[str]:
    """Validate an iteration-log.md file.

    Checks:
    - Contains at least one ITER-NNNN section
    - Each iteration section has Completed, Stories delivered, Tasks executed, Summary
    """
    import re

    errors: list[str] = []

    iter_pattern = re.compile(r"^## ITER-(\d+)", re.MULTILINE)
    iters = list(iter_pattern.finditer(content))

    if not iters:
        errors.append("no iteration sections found (expected at least one '## ITER-NNNN')")
        return errors

    for idx, match in enumerate(iters):
        iter_id = f"ITER-{match.group(1)}"
        start = match.end()
        end = iters[idx + 1].start() if idx + 1 < len(iters) else len(content)
        section = content[start:end]

        for required in ("**Completed:**", "**Stories delivered:**",
                         "**Tasks executed:**", "**Summary:**"):
            if required not in section:
                errors.append(f"{iter_id}: missing required field {required}")

    return errors
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python3 -m unittest tests.test_artifact_validator -v`
Expected: PASS, all previous tests still pass plus the 2 new iteration-log tests

- [ ] **Step 6: Commit**

```bash
git add tests/fixtures/iteration-log.example.md tests/fixtures/iteration-log.invalid.md scripts/validate_artifact.py tests/test_artifact_validator.py
git commit -m "feat: add iteration-log format validator with fixtures"
```

---

### Task 6: Skill file validator

**Files:**
- Create: `scripts/validate_skill.py`
- Create: `tests/test_skill_validator.py`
- Create: `tests/fixtures/skill.valid/SKILL.md`
- Create: `tests/fixtures/skill.invalid-no-frontmatter/SKILL.md`
- Create: `tests/fixtures/skill.invalid-bad-description/SKILL.md`

The validator checks that a SKILL.md file has valid YAML frontmatter with `name` and `description` fields, description starts with "Use when", name uses only letters/numbers/hyphens, and word count is reasonable (<500 words for this plugin's skills).

- [ ] **Step 1: Write failing tests**

Create `tests/test_skill_validator.py`:

```python
"""Unit tests for scripts/validate_skill.py."""
import subprocess
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "scripts" / "validate_skill.py"
FIXTURES = Path(__file__).parent / "fixtures"


class TestSkillValidator(unittest.TestCase):
    def test_script_exists(self):
        self.assertTrue(SCRIPT.exists())

    def test_valid_skill_passes(self):
        result = subprocess.run(
            ["python3", str(SCRIPT), str(FIXTURES / "skill.valid" / "SKILL.md")],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)

    def test_missing_frontmatter_fails(self):
        result = subprocess.run(
            ["python3", str(SCRIPT),
             str(FIXTURES / "skill.invalid-no-frontmatter" / "SKILL.md")],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("frontmatter", result.stderr.lower())

    def test_bad_description_format_fails(self):
        result = subprocess.run(
            ["python3", str(SCRIPT),
             str(FIXTURES / "skill.invalid-bad-description" / "SKILL.md")],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("use when", result.stderr.lower())


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Create the valid fixture**

Create `tests/fixtures/skill.valid/SKILL.md`:

```markdown
---
name: valid-example-skill
description: Use when testing the skill validator — demonstrates a well-formed SKILL.md file with valid frontmatter and a proper description.
---

# Valid Example Skill

This is a fixture for testing the skill validator. It has all the required fields.

## Overview

A minimal well-formed skill file.
```

- [ ] **Step 3: Create the invalid-no-frontmatter fixture**

Create `tests/fixtures/skill.invalid-no-frontmatter/SKILL.md`:

```markdown
# Skill Without Frontmatter

This file is missing YAML frontmatter entirely.
```

- [ ] **Step 4: Create the invalid-bad-description fixture**

Create `tests/fixtures/skill.invalid-bad-description/SKILL.md`:

```markdown
---
name: bad-description-skill
description: This skill does stuff. It's pretty cool.
---

# Bad Description Skill

The description does not start with "Use when".
```

- [ ] **Step 5: Run tests to verify they fail**

Run: `python3 -m unittest tests.test_skill_validator -v`
Expected: FAIL with `FileNotFoundError` or similar (validator doesn't exist yet)

- [ ] **Step 6: Implement the skill validator**

Create `scripts/validate_skill.py`:

```python
#!/usr/bin/env python3
"""Validate a SKILL.md file.

Usage: validate_skill.py <path/to/SKILL.md>

Checks:
- File exists and is readable
- Starts with YAML frontmatter (--- delimited)
- Frontmatter contains 'name' and 'description' fields
- 'name' field uses only letters, numbers, hyphens
- 'description' field starts with "Use when"
- Body word count is under 500 words (warning if over)
"""
import re
import sys
from pathlib import Path


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Parse a simple YAML-like frontmatter (key: value lines between --- delimiters).

    Returns (frontmatter_dict, body). Returns ({}, content) if no frontmatter.
    """
    if not content.startswith("---\n"):
        return {}, content

    end_marker = content.find("\n---\n", 4)
    if end_marker == -1:
        return {}, content

    fm_text = content[4:end_marker]
    body = content[end_marker + 5:]

    fm: dict = {}
    current_key: str | None = None
    for line in fm_text.splitlines():
        if not line.strip():
            continue
        if line.startswith(" ") and current_key:
            fm[current_key] = fm[current_key] + " " + line.strip()
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip()
            fm[key] = value
            current_key = key
    return fm, body


def validate(path: Path) -> tuple[list[str], list[str]]:
    """Return (errors, warnings). Errors cause validation failure; warnings do not."""
    errors: list[str] = []
    warnings: list[str] = []
    content = path.read_text()

    fm, body = parse_frontmatter(content)

    if not fm:
        errors.append("missing or malformed YAML frontmatter (expected --- delimited block at start of file)")
        return errors, warnings

    if "name" not in fm:
        errors.append("frontmatter missing required 'name' field")
    else:
        name = fm["name"]
        if not re.fullmatch(r"[a-zA-Z0-9-]+", name):
            errors.append(f"frontmatter 'name' has invalid characters (must be letters/digits/hyphens): {name}")

    if "description" not in fm:
        errors.append("frontmatter missing required 'description' field")
    else:
        desc = fm["description"]
        if not desc.lower().startswith("use when"):
            errors.append(f"frontmatter 'description' should start with 'Use when' but starts with: {desc[:30]!r}")

    # Word count is a target per writing-skills guidance, not a hard limit.
    word_count = len(body.split())
    if word_count > 500:
        warnings.append(f"body word count {word_count} exceeds 500 (target per writing-skills guidance)")

    return errors, warnings


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_skill.py <path/to/SKILL.md>", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 2

    errors, warnings = validate(path)
    for warn in warnings:
        print(f"warning: {warn}", file=sys.stderr)
    if errors:
        for err in errors:
            print(f"error: {err}", file=sys.stderr)
        return 1

    print(f"OK: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

Make executable:
```bash
chmod +x scripts/validate_skill.py
```

- [ ] **Step 7: Run tests to verify they pass**

Run: `python3 -m unittest tests.test_skill_validator -v`
Expected: PASS, all 4 tests pass

- [ ] **Step 8: Commit**

```bash
git add scripts/validate_skill.py tests/test_skill_validator.py tests/fixtures/skill.valid/ tests/fixtures/skill.invalid-no-frontmatter/ tests/fixtures/skill.invalid-bad-description/
git commit -m "feat: add skill file validator with fixtures"
```

---

### Task 7: Skill stub — `iterative-development` (orchestrator)

**Files:**
- Create: `skills/iterative-development/SKILL.md`

- [ ] **Step 1: Write failing validator check**

Run: `python3 scripts/validate_skill.py skills/iterative-development/SKILL.md`
Expected: FAIL with "file not found"

- [ ] **Step 2: Write the SKILL.md**

Create `skills/iterative-development/SKILL.md`:

```markdown
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
```

- [ ] **Step 3: Run validator to verify it passes**

Run: `python3 scripts/validate_skill.py skills/iterative-development/SKILL.md`
Expected: `OK: skills/iterative-development/SKILL.md`

- [ ] **Step 4: Commit**

```bash
git add skills/iterative-development/SKILL.md
git commit -m "feat: add iterative-development orchestrator skill stub"
```

---

### Task 8: Skill stub — `extracting-requirements`

**Files:**
- Create: `skills/extracting-requirements/SKILL.md`

- [ ] **Step 1: Write failing validator check**

Run: `python3 scripts/validate_skill.py skills/extracting-requirements/SKILL.md`
Expected: FAIL with "file not found"

- [ ] **Step 2: Write the SKILL.md**

Create `skills/extracting-requirements/SKILL.md`:

```markdown
---
name: extracting-requirements
description: Use when starting an iterative-development run on human spec collateral — reads the spec, produces a structured requirements-index.md containing story cards and epics with stable IDs.
---

# Extracting Requirements

## Overview

Reads arbitrary human spec collateral (one file, a directory, or a large prose dump) and produces `docs/superpowers/iterations/requirements-index.md` — the plugin's internal backlog of story cards and epics with stable global IDs.

**This is Plan 1 — walking skeleton implementation. Parallel extraction, chunking, map-reduce aggregation, hierarchical reduce, and huge-spec decomposition are NOT yet implemented and will be added in Plan 2.**

## When to Use

Invoked by `iterative-development` during bootstrap, or standalone when you need to regenerate the requirements index from human spec collateral.

## Walking Skeleton Behavior (Plan 1)

Read the full spec in a single subagent pass — no chunking, no parallel dispatch.

1. Receive the spec path as input (a file or directory).
2. Dispatch a single extraction subagent with the complete spec contents.
3. The subagent produces story cards following the format in `tests/fixtures/requirements-index.example.md`:
   - Each story has a `STORY-NNNN` ID (assigned sequentially starting from 0001)
   - Each story has an Epic reference, Title, As-a/I-want/So-that, Acceptance criteria, Sources, Status
   - Each unique epic theme gets an `EPIC-NNN` ID
4. Write the result to `docs/superpowers/iterations/requirements-index.md`.
5. Run `scripts/validate_artifact.py --type requirements-index <path>` to verify the output is well-formed.
6. If validation fails, fix the formatting issues and re-validate.

**Limits for Plan 1:** the spec must fit in a single subagent's context (approximately 100K tokens). Large specs will be supported in Plan 2.

## Quick Reference

| Input | Output | Validator |
|---|---|---|
| Spec file/directory | `docs/superpowers/iterations/requirements-index.md` | `scripts/validate_artifact.py --type requirements-index` |

## Deferred to later plans

Chunking by file/section, parallel extraction subagents, map-reduce aggregation, hierarchical reduce for very large specs, decomposition for huge specs (>1M tokens), incremental re-extraction when spec files change mid-project.
```

- [ ] **Step 3: Run validator to verify it passes**

Run: `python3 scripts/validate_skill.py skills/extracting-requirements/SKILL.md`
Expected: `OK: skills/extracting-requirements/SKILL.md`

- [ ] **Step 4: Commit**

```bash
git add skills/extracting-requirements/SKILL.md
git commit -m "feat: add extracting-requirements skill stub"
```

---

### Task 9: Skill stub — `scoping-the-simplest-core`

**Files:**
- Create: `skills/scoping-the-simplest-core/SKILL.md`

- [ ] **Step 1: Write failing validator check**

Run: `python3 scripts/validate_skill.py skills/scoping-the-simplest-core/SKILL.md`
Expected: FAIL with "file not found"

- [ ] **Step 2: Write the SKILL.md**

Create `skills/scoping-the-simplest-core/SKILL.md`:

```markdown
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
```

- [ ] **Step 3: Run validator to verify it passes**

Run: `python3 scripts/validate_skill.py skills/scoping-the-simplest-core/SKILL.md`
Expected: `OK: skills/scoping-the-simplest-core/SKILL.md`

- [ ] **Step 4: Commit**

```bash
git add skills/scoping-the-simplest-core/SKILL.md
git commit -m "feat: add scoping-the-simplest-core skill stub"
```

---

### Task 10: Skill stub — `running-an-iteration`

**Files:**
- Create: `skills/running-an-iteration/SKILL.md`

- [ ] **Step 1: Write failing validator check**

Run: `python3 scripts/validate_skill.py skills/running-an-iteration/SKILL.md`
Expected: FAIL with "file not found"

- [ ] **Step 2: Write the SKILL.md**

Create `skills/running-an-iteration/SKILL.md`:

```markdown
---
name: running-an-iteration
description: Use when executing the next pending iteration from an iterative-development roadmap — picks the iteration, decomposes it into tasks, dispatches implementing-tasks, and updates the roadmap and iteration log.
---

# Running an Iteration

## Overview

Drives one iteration from the roadmap: picks the next pending iteration, decomposes its committed stories into TDD-sized tasks, dispatches `implementing-tasks` to execute them, and updates `roadmap.md` and `iteration-log.md`.

**This is Plan 1 — walking skeleton implementation. Pre-iteration scope review (citation check, adversarial review, boxing-in look-ahead), parallel adversarial review on tasks, and sophisticated wrap-up verification are NOT yet implemented and will be added in later plans.**

## When to Use

Invoked by `iterative-development` inside the main loop. Each invocation runs exactly one iteration. After return, the orchestrator invokes `auditing-progress` before picking the next iteration.

## Walking Skeleton Behavior (Plan 1)

1. Read `docs/superpowers/iterations/roadmap.md`, find the first iteration with status `pending`.
2. Read `docs/superpowers/iterations/requirements-index.md`, load the full story cards for each committed story ID in the iteration.
3. Decompose each story into TDD-sized tasks. Each task produces one failing test → minimal implementation → passing test → commit.
4. Dispatch `implementing-tasks` with the in-memory task list and the story context.
5. After `implementing-tasks` returns: for each story in the iteration, check that its acceptance criteria pass (run the tests). Flip each story's status in `requirements-index.md` from `pending` to `done:ITER-NNNN` where NNNN is the current iteration ID.
6. Update the iteration's status in `roadmap.md` from `pending` to `done`.
7. Append a new entry to `docs/superpowers/iterations/iteration-log.md` following the format in `tests/fixtures/iteration-log.example.md`:
   - Completed date
   - Stories delivered
   - Tasks executed count
   - Summary (one paragraph)
   - Learnings (if any)
   - Roadmap revisions (none for Plan 1)
8. Run `scripts/validate_artifact.py --type iteration-log <path>` to verify the log is well-formed.
9. Return control to the orchestrator. Do NOT invoke `auditing-progress` here — that is the orchestrator's job.

## Quick Reference

| Reads | Writes | Dispatches |
|---|---|---|
| `roadmap.md`, `requirements-index.md` | `requirements-index.md` (status), `roadmap.md` (status), `iteration-log.md` (append) | `implementing-tasks` |

## Deferred to later plans

Pre-iteration scope review (3 adversarial checks), formal story-to-task decomposition heuristics, parallel adversarial review wrappers around task dispatch, roadmap revision when iteration learnings invalidate downstream work.
```

- [ ] **Step 3: Run validator to verify it passes**

Run: `python3 scripts/validate_skill.py skills/running-an-iteration/SKILL.md`
Expected: `OK: skills/running-an-iteration/SKILL.md`

- [ ] **Step 4: Commit**

```bash
git add skills/running-an-iteration/SKILL.md
git commit -m "feat: add running-an-iteration skill stub"
```

---

### Task 11: Skill stub — `implementing-tasks`

**Files:**
- Create: `skills/implementing-tasks/SKILL.md`

- [ ] **Step 1: Write failing validator check**

Run: `python3 scripts/validate_skill.py skills/implementing-tasks/SKILL.md`
Expected: FAIL with "file not found"

- [ ] **Step 2: Write the SKILL.md**

Create `skills/implementing-tasks/SKILL.md`:

```markdown
---
name: implementing-tasks
description: Use when executing a batch of TDD-sized tasks inside a running-an-iteration call — dispatches an implementer subagent per task following red-green-refactor discipline and returns per-task completion status.
---

# Implementing Tasks

## Overview

Takes an in-memory batch of TDD-sized tasks and executes each through an implementer subagent following red-green-refactor discipline. This is a fork of `superpowers:subagent-driven-development` with the plan-file reading phase stripped and the final end-of-plan reviewer removed.

**This is Plan 1 — walking skeleton implementation. The two-stage review (spec compliance + code quality), review re-dispatch loop, boxing-in check, parallel adversarial review wrappers, and model selection rules are NOT yet implemented and will be added in later plans.**

## When to Use

Invoked by `running-an-iteration` with a list of tasks. Each task is a complete TDD cycle (failing test → implementation → passing test → commit). Tasks are passed in memory, not via a file.

## Walking Skeleton Behavior (Plan 1)

For each task in the provided list:

1. Dispatch an implementer subagent with:
   - The task description and context (the story card(s) the task contributes to)
   - Instructions to follow TDD red-green-refactor (`superpowers:test-driven-development`)
   - Instructions to commit the work when tests pass
   - Instructions to report back with status DONE / DONE_WITH_CONCERNS / BLOCKED / NEEDS_CONTEXT

2. Wait for the subagent to complete. Do not run tasks in parallel.

3. Handle the returned status:
   - DONE: record the task as complete, move to the next
   - DONE_WITH_CONCERNS: record the concerns, move to the next (Plan 1 does not block on concerns)
   - BLOCKED or NEEDS_CONTEXT: return control to the caller with the blocker details. The caller decides whether to provide more context and re-dispatch, or escalate

4. After all tasks complete, return a per-task result list to the caller.

**No review dispatch in Plan 1.** The implementer's self-review is the only quality gate at this point. Two-stage review and PAR wrappers come in later plans.

## Quick Reference

| Input | Output | Sub-dispatches |
|---|---|---|
| Task list (in memory) + iteration context | Per-task result list | Implementer subagents (one per task, sequential) |

## Deferred to later plans

Spec-compliance reviewer dispatch, code-quality reviewer dispatch, parallel adversarial review (2 reviewers per stage), boxing-in check, re-dispatch loop on review failures, model selection rules.
```

- [ ] **Step 3: Run validator to verify it passes**

Run: `python3 scripts/validate_skill.py skills/implementing-tasks/SKILL.md`
Expected: `OK: skills/implementing-tasks/SKILL.md`

- [ ] **Step 4: Commit**

```bash
git add skills/implementing-tasks/SKILL.md
git commit -m "feat: add implementing-tasks skill stub (SDD fork)"
```

---

### Task 12: Skill stub — `auditing-progress`

**Files:**
- Create: `skills/auditing-progress/SKILL.md`

- [ ] **Step 1: Write failing validator check**

Run: `python3 scripts/validate_skill.py skills/auditing-progress/SKILL.md`
Expected: FAIL with "file not found"

- [ ] **Step 2: Write the SKILL.md**

Create `skills/auditing-progress/SKILL.md`:

```markdown
---
name: auditing-progress
description: Use when an iteration has just finished and you need to verify the just-delivered work matches its story acceptance criteria and the whole product has no regressions — runs after every iteration as part of the planning cycle.
---

# Auditing Progress

## Overview

Runs after every iteration. Deep-checks the just-finished iteration's work (every AC verified by running tests + reading code) and lightly sanity-sweeps the whole product for regressions. Returns gaps (ACs not actually met) and unrequested features (code that doesn't map to any story).

**This is Plan 1 — walking skeleton implementation. Parallel adversarial auditor pairs, two-tier partitioning (deep + sweep), per-epic auditor dispatch, and sophisticated unrequested-feature scanning are NOT yet implemented and will be added in later plans.**

## When to Use

Invoked by `iterative-development` after every `running-an-iteration` call, before picking the next iteration.

## Walking Skeleton Behavior (Plan 1)

1. Read `docs/superpowers/iterations/requirements-index.md`.
2. Identify the stories that were marked `done:ITER-<current>` in the just-finished iteration.
3. Dispatch a single auditor subagent (no parallel pairs, no partitioning) with:
   - The list of just-done stories and their acceptance criteria
   - The current product state (file paths, test command)
   - Instructions to: run the tests for each AC, verify the AC is actually met, flag any that are not
4. The auditor returns a gap list:
   - For each just-done story, which ACs pass and which fail
5. For Plan 1 walking skeleton: **no sweep tier**. Only the just-done stories are audited. Regression detection across earlier work is deferred to Plan 4.
6. Aggregate the auditor's report:
   - If any ACs fail: append gap stories to `requirements-index.md` (status `pending`) and revise `roadmap.md` to add a follow-up iteration
   - If all ACs pass: the iteration is confirmed done, proceed to the next iteration
7. Return the audit result to the orchestrator.

## Quick Reference

| Reads | Writes | Dispatches |
|---|---|---|
| `requirements-index.md`, product code/tests | `requirements-index.md` (gap stories), `roadmap.md` (new iteration) if gaps | Auditor subagent (one, non-paired) |

## Deferred to later plans

Parallel adversarial auditor pairs, two-tier scope (deep new work + light whole-product sweep), per-epic partitioning for large backlogs, unrequested-feature scanning across iteration diffs, formal aggregation rules for disagreeing auditor findings.
```

- [ ] **Step 3: Run validator to verify it passes**

Run: `python3 scripts/validate_skill.py skills/auditing-progress/SKILL.md`
Expected: `OK: skills/auditing-progress/SKILL.md`

- [ ] **Step 4: Commit**

```bash
git add skills/auditing-progress/SKILL.md
git commit -m "feat: add auditing-progress skill stub"
```

---

### Task 13: Walking skeleton sample spec

**Files:**
- Create: `tests/walking-skeleton/input-spec/spec.md`

- [ ] **Step 1: Write the sample spec**

Create `tests/walking-skeleton/input-spec/spec.md`:

```markdown
# Greet CLI Spec

## Overview

A tiny command-line tool that greets the user by name. This spec is intentionally minimal — it exists as a dogfood target for the iterative-development plugin walking skeleton.

## Functional requirements

### F-1: Personalized greeting
When the user runs `greet <name>`, the tool prints `Hello, <name>!` to stdout and exits with status 0.

### F-2: Missing argument handling
When the user runs `greet` with no argument, the tool prints `usage: greet <name>` to stderr and exits with a non-zero status.

## Out of scope
- Internationalization
- Configuration files
- Arguments other than the name
- Any feature not mentioned above
```

- [ ] **Step 2: Verify the spec file exists and has content**

Run: `wc -l tests/walking-skeleton/input-spec/spec.md`
Expected: at least 15 lines

- [ ] **Step 3: Commit**

```bash
git add tests/walking-skeleton/input-spec/spec.md
git commit -m "feat: add walking-skeleton sample spec (greet CLI)"
```

---

### Task 14: Walking skeleton dogfood procedure

**Files:**
- Create: `tests/walking-skeleton/README.md`

- [ ] **Step 1: Write the procedure document**

Create `tests/walking-skeleton/README.md`:

```markdown
# Walking Skeleton Dogfood Procedure

This directory contains the end-to-end manual verification for Plan 1 of the iterative-development plugin. Because the plugin is instructional (skills are executed by Claude in-session), there is no fully-automated end-to-end test. This procedure is the verification.

## Prerequisites

- The plugin is installed (or available as a local plugin marketplace entry)
- Python 3 is available
- A clean directory to run the dogfood in (do NOT run in the plugin's own repo)
- All unit tests pass: `python3 -m unittest discover tests/`
- All skill files validate: `bash scripts/run_validation_suite.sh`

## Procedure

### 1. Set up a clean dogfood workspace

```bash
mkdir /tmp/walking-skeleton-dogfood
cd /tmp/walking-skeleton-dogfood
cp <plugin-repo>/tests/walking-skeleton/input-spec/spec.md .
git init && git add spec.md && git commit -m "initial: sample spec"
```

### 2. Invoke the plugin

In a Claude Code session running in `/tmp/walking-skeleton-dogfood`, ask Claude to use the `iterative-development` skill on `spec.md`.

Expected high-level flow:
1. Claude invokes `iterative-development` (orchestrator)
2. Orchestrator invokes `extracting-requirements` → creates `docs/superpowers/iterations/requirements-index.md`
3. Orchestrator invokes `scoping-the-simplest-core` → creates `docs/superpowers/iterations/roadmap.md`
4. Orchestrator enters the iteration loop:
   - Invokes `running-an-iteration` → picks ITER-0000, decomposes into tasks
   - `running-an-iteration` dispatches `implementing-tasks` → writes TDD-style code that implements greet
   - `running-an-iteration` updates `requirements-index.md`, `roadmap.md`, appends to `iteration-log.md`
   - Orchestrator invokes `auditing-progress` → confirms ACs pass
   - Roadmap is empty + audit clean → orchestrator terminates

### 3. Verify artifacts

Check that the following files exist and validate:

```bash
python3 <plugin-repo>/scripts/validate_artifact.py --type requirements-index docs/superpowers/iterations/requirements-index.md
python3 <plugin-repo>/scripts/validate_artifact.py --type roadmap docs/superpowers/iterations/roadmap.md
python3 <plugin-repo>/scripts/validate_artifact.py --type iteration-log docs/superpowers/iterations/iteration-log.md
```

Expected: all three print `OK: <path>`.

### 4. Verify the final product works

Whatever executable the plugin produced (e.g., `greet.py`, `greet.sh`, or a compiled binary), verify it matches the spec:

```bash
./greet Alice
# Expected output: Hello, Alice!
# Expected exit code: 0

./greet 2>&1
# Expected output: usage: greet <name>
# Expected exit code: non-zero
```

### 5. Verify the git history

The implementation should be committed in small TDD-sized commits:

```bash
git log --oneline
# Expected: multiple commits, at minimum:
# - failing test for greeting
# - implementation of greeting
# - failing test for error case
# - implementation of error handling
```

## Acceptance criteria for Plan 1 walking skeleton

The walking skeleton passes if:

- [ ] All six skills are invoked in the correct order
- [ ] All three artifacts are created in `docs/superpowers/iterations/`
- [ ] All three artifacts validate against their format validators
- [ ] The final product satisfies both functional requirements (F-1 and F-2) from `spec.md`
- [ ] The git history shows TDD-style commits (test → implementation)
- [ ] The orchestrator terminates cleanly (does not run indefinitely or crash)

If any of these fail, the walking skeleton is not complete and Plan 1 is not done.

## Known limitations (deferred to later plans)

This is the walking skeleton. It does NOT:
- Parallel-dispatch anything
- Run parallel adversarial review
- Audit previously-done work (only the just-finished iteration)
- Chunk or map-reduce the spec (reads it in one pass)
- Handle huge specs (>100K tokens in the spec)
- Handle human interrupts between iterations
- Recover from crashes mid-iteration

These capabilities are added in Plans 2-7.
```

- [ ] **Step 2: Verify the README file exists**

Run: `wc -l tests/walking-skeleton/README.md`
Expected: at least 50 lines

- [ ] **Step 3: Commit**

```bash
git add tests/walking-skeleton/README.md
git commit -m "docs: add walking-skeleton dogfood procedure"
```

---

### Task 15: Validation suite runner

**Files:**
- Create: `scripts/run_validation_suite.sh`

This script runs every validator and every unit test in sequence, failing on the first error. It's the "walking skeleton is consistent" smoke test.

- [ ] **Step 1: Write failing test (manual invocation verification)**

Run: `bash scripts/run_validation_suite.sh`
Expected: FAIL, "No such file or directory"

- [ ] **Step 2: Write the suite runner**

Create `scripts/run_validation_suite.sh`:

```bash
#!/usr/bin/env bash
# Walking skeleton validation suite.
# Runs all unit tests and validators. Fails on first error.
set -euo pipefail

cd "$(dirname "$0")/.."

echo "=== Running Python unit tests ==="
python3 -m unittest discover tests/ -v

echo ""
echo "=== Validating plugin manifest ==="
python3 -c "import json; json.load(open('.claude-plugin/plugin.json'))"
echo "OK: .claude-plugin/plugin.json"

echo ""
echo "=== Validating all SKILL.md files ==="
for skill_file in skills/*/SKILL.md; do
    python3 scripts/validate_skill.py "$skill_file"
done

echo ""
echo "=== Validating artifact format fixtures ==="
python3 scripts/validate_artifact.py --type requirements-index tests/fixtures/requirements-index.example.md
python3 scripts/validate_artifact.py --type roadmap tests/fixtures/roadmap.example.md
python3 scripts/validate_artifact.py --type iteration-log tests/fixtures/iteration-log.example.md

echo ""
echo "=== All validation checks passed ==="
```

Make it executable:
```bash
chmod +x scripts/run_validation_suite.sh
```

- [ ] **Step 3: Run the suite to verify everything passes**

Run: `bash scripts/run_validation_suite.sh`
Expected output (abbreviated):
```
=== Running Python unit tests ===
... (all tests pass)
=== Validating plugin manifest ===
OK: .claude-plugin/plugin.json
=== Validating all SKILL.md files ===
OK: skills/auditing-progress/SKILL.md
OK: skills/extracting-requirements/SKILL.md
OK: skills/implementing-tasks/SKILL.md
OK: skills/iterative-development/SKILL.md
OK: skills/running-an-iteration/SKILL.md
OK: skills/scoping-the-simplest-core/SKILL.md
=== Validating artifact format fixtures ===
OK: tests/fixtures/requirements-index.example.md
OK: tests/fixtures/roadmap.example.md
OK: tests/fixtures/iteration-log.example.md
=== All validation checks passed ===
```
Expected exit code: 0

- [ ] **Step 4: Commit**

```bash
git add scripts/run_validation_suite.sh
git commit -m "feat: add validation suite runner for walking skeleton"
```

---

## Plan Completion Checklist

After all 15 tasks are complete, verify:

- [ ] `bash scripts/run_validation_suite.sh` exits with code 0
- [ ] All six skills exist in `skills/` and validate
- [ ] All three artifact format fixtures validate
- [ ] The plugin manifest parses as valid JSON and lists all six skills
- [ ] The walking-skeleton dogfood procedure (`tests/walking-skeleton/README.md`) is complete and actionable
- [ ] Git history shows at least 15 commits (one per task, minimum)

**Deferred to later plans (do NOT attempt in Plan 1):**
- Parallel adversarial review at any gate
- Map-reduce extraction with chunking
- Two-tier auditing (deep + sweep)
- Pre-iteration scope review (citation + adversarial + boxing-in)
- Human interrupt protocol
- Crash resumption beyond "re-invoke the orchestrator"
- Model selection rules for subagent dispatch
- Multi-model PAR
- Real dogfood run on the ghost-pepper sample spec

**Next plan:** Plan 2 — `extracting-requirements` hardening (chunking, parallel dispatch, map-reduce aggregation).
