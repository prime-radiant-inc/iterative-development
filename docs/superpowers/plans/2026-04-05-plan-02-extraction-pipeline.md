# Extraction Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the single-pass extraction stub (Plan 1) with a chunking + parallel-dispatch + aggregation pipeline that handles medium-to-large specs (10K–100K tokens, ~50+ files) without any single agent holding the full spec in context.

**Architecture:** Three new Python scripts form the extraction pipeline backbone: `chunk_spec.py` splits spec files into heading-based chunks, extraction subagents process chunks in parallel using a prompt template, and `aggregate_stories.py` deduplicates and merges extracted stories into `requirements-index.md`. The updated `extracting-requirements` SKILL.md orchestrates this pipeline. All scripts are Python 3 stdlib only (no external deps).

**Tech Stack:** Python 3 (stdlib: json, re, argparse, pathlib, collections), Markdown, Shell

---

## What Plan 2 Adds

Plan 1 delivered a walking skeleton where `extracting-requirements` reads the entire spec in one subagent pass. Plan 2 replaces that with:

1. **`scripts/chunk_spec.py`** — splits spec files by markdown headings, estimates token counts, produces JSON chunk list
2. **`skills/extracting-requirements/extraction-subagent-prompt.md`** — prompt template for extraction subagents (defines what each subagent receives and what it returns)
3. **`scripts/aggregate_stories.py`** — takes multiple JSON files of extracted story proposals, deduplicates by title, groups into epics, assigns stable STORY-NNNN / EPIC-NNN IDs, outputs `requirements-index.md`
4. **Updated `skills/extracting-requirements/SKILL.md`** — full pipeline instructions replacing the walking-skeleton stub

**Deferred to later plans:** hierarchical reduce (specs >1M tokens), huge-spec decomposition (sub-project identification), incremental re-extraction (mid-project spec changes).

---

## File Structure

```
scripts/
  chunk_spec.py              # NEW: split spec files into heading-based chunks
  aggregate_stories.py       # NEW: merge extracted story JSONs → requirements-index.md
  validate_artifact.py       # EXISTS (no changes)
  run_validation_suite.sh    # MODIFY: add new tests

skills/
  extracting-requirements/
    SKILL.md                            # MODIFY: replace walking-skeleton behavior
    extraction-subagent-prompt.md       # NEW: prompt template for extraction subagents

tests/
  test_chunk_spec.py                    # NEW: unit tests for chunking
  test_aggregate_stories.py             # NEW: unit tests for aggregation
  test_extraction_pipeline.py           # NEW: end-to-end pipeline test (chunk→aggregate→validate)
  fixtures/
    multi-file-spec/                    # NEW: synthetic multi-file spec for testing
      overview.md
      domain-users.md
      domain-billing.md
    extracted-stories-sample.json       # NEW: sample extraction output for aggregation tests
```

---

## Task Summary

| # | Task | Files |
|---|---|---|
| 1 | Chunking script | `scripts/chunk_spec.py`, `tests/test_chunk_spec.py` |
| 2 | Multi-file spec fixture | `tests/fixtures/multi-file-spec/overview.md`, `domain-users.md`, `domain-billing.md` |
| 3 | Extraction subagent prompt template | `skills/extracting-requirements/extraction-subagent-prompt.md` |
| 4 | Extracted stories fixture | `tests/fixtures/extracted-stories-sample.json` |
| 5 | Aggregation script | `scripts/aggregate_stories.py`, `tests/test_aggregate_stories.py` |
| 6 | Pipeline integration test | `tests/test_extraction_pipeline.py` |
| 7 | Update extracting-requirements SKILL.md | `skills/extracting-requirements/SKILL.md` |
| 8 | Update validation suite | `scripts/run_validation_suite.sh` |

---

### Task 1: Chunking script

**Files:**
- Create: `scripts/chunk_spec.py`
- Create: `tests/test_chunk_spec.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_chunk_spec.py`:

```python
"""Unit tests for scripts/chunk_spec.py."""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "scripts" / "chunk_spec.py"


class TestChunkSpec(unittest.TestCase):
    def test_script_exists(self):
        self.assertTrue(SCRIPT.exists())

    def test_small_file_is_single_chunk(self):
        """A file under the token threshold should produce exactly one chunk."""
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
            f.write("# Small Spec\n\nJust a few words here.\n")
            tmp = f.name
        try:
            result = subprocess.run(
                ["python3", str(SCRIPT), tmp],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            chunks = json.loads(result.stdout)
            self.assertEqual(len(chunks), 1)
            self.assertIn("Small Spec", chunks[0]["content"])
            self.assertEqual(chunks[0]["source_file"], tmp)
        finally:
            Path(tmp).unlink()

    def test_file_with_headings_splits_by_h2(self):
        """A file over the token threshold with ## headings should split by heading."""
        # Create content big enough to trigger splitting (>3K words ≈ >4K tokens)
        section_a = "## Section A\n\n" + ("word " * 2000) + "\n\n"
        section_b = "## Section B\n\n" + ("word " * 2000) + "\n\n"
        content = "# Big Spec\n\nPreamble text.\n\n" + section_a + section_b

        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
            f.write(content)
            tmp = f.name
        try:
            result = subprocess.run(
                ["python3", str(SCRIPT), tmp, "--max-tokens", "3000"],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            chunks = json.loads(result.stdout)
            # Should have preamble + Section A + Section B = 3 chunks
            self.assertGreaterEqual(len(chunks), 2)
            headings = [c["heading"] for c in chunks]
            self.assertIn("Section A", headings)
            self.assertIn("Section B", headings)
        finally:
            Path(tmp).unlink()

    def test_directory_processes_all_md_files(self):
        """A directory should produce chunks from all .md files in it."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "a.md").write_text("# File A\n\nContent A.\n")
            (Path(tmpdir) / "b.md").write_text("# File B\n\nContent B.\n")
            (Path(tmpdir) / "c.txt").write_text("Not markdown, should be ignored.\n")

            result = subprocess.run(
                ["python3", str(SCRIPT), tmpdir],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            chunks = json.loads(result.stdout)
            source_files = {c["source_file"] for c in chunks}
            self.assertEqual(len(source_files), 2)  # only .md files
            self.assertTrue(all("Content" in c["content"] for c in chunks))

    def test_missing_path_returns_error(self):
        result = subprocess.run(
            ["python3", str(SCRIPT), "/tmp/does-not-exist-99999"],
            capture_output=True, text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not found", result.stderr.lower())

    def test_each_chunk_has_required_fields(self):
        """Every chunk must have source_file, heading, start_line, end_line, content, estimated_tokens."""
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
            f.write("# Test\n\nHello world.\n")
            tmp = f.name
        try:
            result = subprocess.run(
                ["python3", str(SCRIPT), tmp],
                capture_output=True, text=True,
            )
            chunks = json.loads(result.stdout)
            for chunk in chunks:
                for field in ("source_file", "heading", "start_line", "end_line",
                              "content", "estimated_tokens"):
                    self.assertIn(field, chunk, f"missing field: {field}")
        finally:
            Path(tmp).unlink()


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest tests.test_chunk_spec -v`
Expected: FAIL with `AssertionError: ... chunk_spec.py does not exist`

- [ ] **Step 3: Implement the chunking script**

Create `scripts/chunk_spec.py`:

```python
#!/usr/bin/env python3
"""Chunk spec files into sections for parallel extraction.

Usage: chunk_spec.py <path> [--max-tokens 4000]

If <path> is a file, chunks that single file.
If <path> is a directory, chunks all .md files recursively.

Output: JSON array of chunks to stdout. Each chunk has:
  source_file, heading, start_line, end_line, content, estimated_tokens

Chunking strategy:
  Files < max_tokens: single chunk (whole file)
  Files >= max_tokens: split by ## headings
  Sections still over max_tokens: split by ### headings
"""
import argparse
import json
import re
import sys
from pathlib import Path


def estimate_tokens(text: str) -> int:
    """Estimate token count. Conservative: 1 word ~ 1.3 tokens."""
    return int(len(text.split()) * 1.3)


def split_by_heading(content: str, level: int) -> list[dict]:
    """Split markdown by heading level. Returns list of {heading, content}."""
    prefix = "#" * level
    pattern = re.compile(rf"^{prefix} (.+)$", re.MULTILINE)
    matches = list(pattern.finditer(content))

    if not matches:
        return [{"heading": None, "content": content}]

    sections: list[dict] = []

    # Preamble before first heading
    if matches[0].start() > 0:
        preamble = content[: matches[0].start()].strip()
        if preamble:
            sections.append({"heading": "(preamble)", "content": preamble})

    for idx, match in enumerate(matches):
        start = match.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(content)
        sections.append({
            "heading": match.group(1).strip(),
            "content": content[start:end].strip(),
        })

    return sections


def find_line_range(full_content: str, section_content: str) -> tuple[int, int]:
    """Find the start and end line numbers of section_content within full_content."""
    pos = full_content.find(section_content[:80])
    if pos == -1:
        return 1, full_content.count("\n") + 1
    start_line = full_content[:pos].count("\n") + 1
    end_line = start_line + section_content.count("\n")
    return start_line, end_line


def chunk_file(path: Path, max_tokens: int) -> list[dict]:
    """Chunk a single file into sections."""
    content = path.read_text()
    tokens = estimate_tokens(content)

    if tokens <= max_tokens:
        return [{
            "source_file": str(path),
            "heading": None,
            "start_line": 1,
            "end_line": content.count("\n") + 1,
            "content": content,
            "estimated_tokens": tokens,
        }]

    # Split by ## headings
    sections = split_by_heading(content, level=2)
    chunks: list[dict] = []

    for section in sections:
        sec_tokens = estimate_tokens(section["content"])
        start_line, end_line = find_line_range(content, section["content"])

        if sec_tokens <= max_tokens:
            chunks.append({
                "source_file": str(path),
                "heading": section["heading"],
                "start_line": start_line,
                "end_line": end_line,
                "content": section["content"],
                "estimated_tokens": sec_tokens,
            })
        else:
            # Sub-split by ### headings
            subsections = split_by_heading(section["content"], level=3)
            for subsec in subsections:
                sub_tokens = estimate_tokens(subsec["content"])
                sub_start, sub_end = find_line_range(content, subsec["content"])
                heading = section["heading"]
                if subsec["heading"] and subsec["heading"] != "(preamble)":
                    heading = f"{heading} > {subsec['heading']}"
                chunks.append({
                    "source_file": str(path),
                    "heading": heading,
                    "start_line": sub_start,
                    "end_line": sub_end,
                    "content": subsec["content"],
                    "estimated_tokens": sub_tokens,
                })

    return chunks


def chunk_path(path: Path, max_tokens: int) -> list[dict]:
    """Chunk a file or directory."""
    if path.is_file():
        return chunk_file(path, max_tokens)
    if path.is_dir():
        chunks: list[dict] = []
        for md_file in sorted(path.rglob("*.md")):
            chunks.extend(chunk_file(md_file, max_tokens))
        return chunks
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description="Chunk spec files for extraction")
    parser.add_argument("path", help="File or directory to chunk")
    parser.add_argument("--max-tokens", type=int, default=4000,
                        help="Max tokens per chunk (default 4000)")
    args = parser.parse_args()

    path = Path(args.path)
    if not path.exists():
        print(f"error: path not found: {path}", file=sys.stderr)
        return 2

    chunks = chunk_path(path, args.max_tokens)
    json.dump(chunks, sys.stdout, indent=2)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

Make it executable:
```bash
chmod +x scripts/chunk_spec.py
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest tests.test_chunk_spec -v`
Expected: PASS, all 6 tests pass

Also verify no regressions: `python3 -m unittest discover tests/ -v`
Expected: all 21 tests pass (15 from Plan 1 + 6 new)

- [ ] **Step 5: Commit**

```bash
git add scripts/chunk_spec.py tests/test_chunk_spec.py
git commit -m "feat: add chunk_spec.py for heading-based spec splitting"
```

---

### Task 2: Multi-file spec fixture

**Files:**
- Create: `tests/fixtures/multi-file-spec/overview.md`
- Create: `tests/fixtures/multi-file-spec/domain-users.md`
- Create: `tests/fixtures/multi-file-spec/domain-billing.md`

This fixture simulates a medium-sized spec split across multiple files — the kind of input that requires chunking.

- [ ] **Step 1: Create overview.md**

Create `tests/fixtures/multi-file-spec/overview.md`:

```markdown
# TaskTracker Spec

## Overview

TaskTracker is a command-line task management tool. Users can create, list, complete, and delete tasks.

## Architecture

Tasks are stored as JSON in a local file (`~/.tasktracker/tasks.json`). The CLI provides subcommands for each operation.

## Out of Scope

- Cloud sync
- Multi-user support
- GUI
```

- [ ] **Step 2: Create domain-users.md**

Create `tests/fixtures/multi-file-spec/domain-users.md`:

```markdown
# User-Facing Commands

## Creating Tasks

When the user runs `task add <title>`, a new task is created with:
- A unique numeric ID (auto-incremented)
- The provided title
- Status: "pending"
- Creation timestamp

The tool prints `Created task #<id>: <title>` to stdout and exits 0.

If no title is provided, print `usage: task add <title>` to stderr and exit 1.

## Listing Tasks

When the user runs `task list`, all tasks are displayed in a table:
```
ID  Status   Title
1   pending  Buy groceries
2   done     Write tests
```

If no tasks exist, print `No tasks.` and exit 0.

## Completing Tasks

When the user runs `task done <id>`, the task with that ID is marked as "done".

Print `Completed task #<id>: <title>` to stdout and exit 0.

If the ID doesn't exist, print `error: task #<id> not found` to stderr and exit 1.
```

- [ ] **Step 3: Create domain-billing.md**

Create `tests/fixtures/multi-file-spec/domain-billing.md`:

```markdown
# Billing Integration

## Usage Tracking

When a task is created, increment the monthly task counter in `~/.tasktracker/usage.json`.

The counter resets on the first of each month.

## Quota Enforcement

If the user has created more than 100 tasks in the current month, `task add` should print `error: monthly quota exceeded (100 tasks)` to stderr and exit 1.

No task is created when the quota is exceeded.
```

- [ ] **Step 4: Verify the fixture works with chunk_spec.py**

Run: `python3 scripts/chunk_spec.py tests/fixtures/multi-file-spec/ | python3 -c "import json,sys; chunks=json.load(sys.stdin); print(f'{len(chunks)} chunks from {len(set(c[\"source_file\"] for c in chunks))} files')"`
Expected: `3 chunks from 3 files` (each file is small enough to be one chunk)

- [ ] **Step 5: Commit**

```bash
git add tests/fixtures/multi-file-spec/
git commit -m "test: add multi-file spec fixture for extraction pipeline"
```

---

### Task 3: Extraction subagent prompt template

**Files:**
- Create: `skills/extracting-requirements/extraction-subagent-prompt.md`

This is the prompt that each extraction subagent receives. It tells the subagent what to read, what format to return, and what NOT to do (no IDs, no dedup — that's the aggregator's job).

- [ ] **Step 1: Write the prompt template**

Create `skills/extracting-requirements/extraction-subagent-prompt.md`:

````markdown
# Extraction Subagent Prompt Template

Use this template when dispatching an extraction subagent. Fill in the bracketed values.

```
Agent tool (general-purpose):
  description: "Extract stories from [source description]"
  prompt: |
    You are extracting testable requirements from spec documentation.

    ## Your Input

    The following spec content is from [source_file] (lines [start_line]-[end_line]):

    ---
    [chunk content pasted here]
    ---

    ## Your Job

    Read the spec content above and extract every testable requirement as a
    story card. For each distinct requirement you find, produce a story in
    this EXACT JSON format:

    {
      "stories": [
        {
          "title": "Short imperative title (e.g., 'User creates a new task')",
          "epic_theme": "Domain grouping theme (e.g., 'Task Management')",
          "as_a": "actor role (e.g., 'command-line user')",
          "i_want": "capability (e.g., 'to run task add <title>')",
          "so_that": "benefit (e.g., 'a new task is created and tracked')",
          "acceptance_criteria": [
            "AC-1: Specific testable criterion with expected behavior",
            "AC-2: Another testable criterion"
          ],
          "sources": [
            {"file": "[source_file]", "lines": "[relevant line range]"}
          ]
        }
      ]
    }

    ## Rules

    - Every story MUST have at least one acceptance criterion that is directly testable
    - Acceptance criteria must describe observable behavior (input → expected output)
    - Sources must cite the specific file and line range where the requirement appears
    - Propose an epic_theme for grouping related stories — use a short domain name
    - Do NOT assign STORY-NNNN or EPIC-NNN IDs — the aggregator does that
    - Do NOT attempt deduplication — the aggregator handles that
    - Do NOT invent requirements not present in the spec content
    - If the spec is ambiguous, extract what is clearly stated and note the ambiguity
    - Output ONLY the JSON object. No other text, no markdown fences, no explanation.
```
````

- [ ] **Step 2: Validate the file exists and is well-formed**

Run: `wc -l skills/extracting-requirements/extraction-subagent-prompt.md`
Expected: at least 40 lines

- [ ] **Step 3: Commit**

```bash
git add skills/extracting-requirements/extraction-subagent-prompt.md
git commit -m "feat: add extraction subagent prompt template"
```

---

### Task 4: Extracted stories sample fixture

**Files:**
- Create: `tests/fixtures/extracted-stories-sample.json`

This fixture represents what two extraction subagents would return after processing the `domain-users.md` and `domain-billing.md` chunks. It's used by the aggregation tests in Task 5.

- [ ] **Step 1: Create the fixture**

Create `tests/fixtures/extracted-stories-sample.json`:

```json
[
  {
    "title": "User creates a new task",
    "epic_theme": "Task Management",
    "as_a": "command-line user",
    "i_want": "to run task add <title> to create a task",
    "so_that": "the task is tracked with a unique ID and pending status",
    "acceptance_criteria": [
      "AC-1: Running `task add Buy groceries` prints `Created task #1: Buy groceries` to stdout and exits 0",
      "AC-2: Running `task add` with no title prints `usage: task add <title>` to stderr and exits 1"
    ],
    "sources": [
      {"file": "domain-users.md", "lines": "3-12"}
    ]
  },
  {
    "title": "User lists all tasks",
    "epic_theme": "Task Management",
    "as_a": "command-line user",
    "i_want": "to run task list to see all tasks",
    "so_that": "I can see what needs to be done",
    "acceptance_criteria": [
      "AC-1: Running `task list` with tasks shows a table with ID, Status, Title columns",
      "AC-2: Running `task list` with no tasks prints `No tasks.` and exits 0"
    ],
    "sources": [
      {"file": "domain-users.md", "lines": "14-23"}
    ]
  },
  {
    "title": "User completes a task",
    "epic_theme": "Task Management",
    "as_a": "command-line user",
    "i_want": "to run task done <id> to mark a task as completed",
    "so_that": "I can track my progress",
    "acceptance_criteria": [
      "AC-1: Running `task done 1` marks task #1 as done and prints confirmation",
      "AC-2: Running `task done 999` for a non-existent ID prints error to stderr and exits 1"
    ],
    "sources": [
      {"file": "domain-users.md", "lines": "25-31"}
    ]
  },
  {
    "title": "Usage tracking increments on task creation",
    "epic_theme": "Billing",
    "as_a": "system",
    "i_want": "the monthly task counter to increment when a task is created",
    "so_that": "usage can be tracked for quota enforcement",
    "acceptance_criteria": [
      "AC-1: Creating a task increments the counter in usage.json",
      "AC-2: The counter resets on the first of each month"
    ],
    "sources": [
      {"file": "domain-billing.md", "lines": "3-7"}
    ]
  },
  {
    "title": "Quota enforcement blocks task creation over limit",
    "epic_theme": "Billing",
    "as_a": "system",
    "i_want": "task add to fail when the monthly quota is exceeded",
    "so_that": "usage limits are enforced",
    "acceptance_criteria": [
      "AC-1: With 100+ tasks this month, `task add` prints quota error to stderr and exits 1",
      "AC-2: No task is created when quota is exceeded"
    ],
    "sources": [
      {"file": "domain-billing.md", "lines": "9-13"}
    ]
  }
]
```

- [ ] **Step 2: Verify it parses as valid JSON**

Run: `python3 -c "import json; data=json.load(open('tests/fixtures/extracted-stories-sample.json')); print(f'{len(data)} stories')"`
Expected: `5 stories`

- [ ] **Step 3: Commit**

```bash
git add tests/fixtures/extracted-stories-sample.json
git commit -m "test: add extracted stories sample fixture for aggregation tests"
```

---

### Task 5: Aggregation script

**Files:**
- Create: `scripts/aggregate_stories.py`
- Create: `tests/test_aggregate_stories.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_aggregate_stories.py`:

```python
"""Unit tests for scripts/aggregate_stories.py."""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "scripts" / "aggregate_stories.py"
FIXTURES = Path(__file__).parent / "fixtures"
VALIDATOR = Path(__file__).parent.parent / "scripts" / "validate_artifact.py"


class TestAggregateStories(unittest.TestCase):
    def test_script_exists(self):
        self.assertTrue(SCRIPT.exists())

    def test_sample_fixture_produces_valid_index(self):
        """Aggregating the sample fixture should produce a valid requirements-index.md."""
        result = subprocess.run(
            ["python3", str(SCRIPT), str(FIXTURES / "extracted-stories-sample.json")],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        output = result.stdout
        # Should contain story and epic headers
        self.assertIn("## STORY-0001", output)
        self.assertIn("## EPIC-", output)
        # Validate the output with the artifact validator
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
            f.write(output)
            tmp = f.name
        try:
            val_result = subprocess.run(
                ["python3", str(VALIDATOR), "--type", "requirements-index", tmp],
                capture_output=True, text=True,
            )
            self.assertEqual(val_result.returncode, 0,
                             msg=f"Validator failed: {val_result.stderr}")
        finally:
            Path(tmp).unlink()

    def test_dedup_merges_duplicate_titles(self):
        """Stories with identical titles should be merged, sources combined."""
        stories = [
            {
                "title": "Same Story",
                "epic_theme": "Test",
                "as_a": "user", "i_want": "x", "so_that": "y",
                "acceptance_criteria": ["AC-1: test"],
                "sources": [{"file": "a.md", "lines": "1-5"}]
            },
            {
                "title": "Same Story",
                "epic_theme": "Test",
                "as_a": "user", "i_want": "x", "so_that": "y",
                "acceptance_criteria": ["AC-1: test"],
                "sources": [{"file": "b.md", "lines": "10-15"}]
            },
        ]
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump(stories, f)
            tmp = f.name
        try:
            result = subprocess.run(
                ["python3", str(SCRIPT), tmp],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            output = result.stdout
            # Should have exactly ONE STORY (deduped)
            self.assertEqual(output.count("## STORY-"), 1)
            # But should cite both sources
            self.assertIn("a.md", output)
            self.assertIn("b.md", output)
        finally:
            Path(tmp).unlink()

    def test_epics_grouped_by_theme(self):
        """Stories with different epic_themes get different EPIC IDs."""
        result = subprocess.run(
            ["python3", str(SCRIPT), str(FIXTURES / "extracted-stories-sample.json")],
            capture_output=True, text=True,
        )
        output = result.stdout
        # Sample has 2 themes: "Task Management" (3 stories) and "Billing" (2 stories)
        self.assertIn("Task Management", output)
        self.assertIn("Billing", output)
        # Should have 2 epics
        import re
        epic_ids = re.findall(r"## EPIC-\d+", output)
        self.assertEqual(len(epic_ids), 2)

    def test_story_ids_are_sequential(self):
        """Story IDs should be assigned sequentially starting from 0001."""
        result = subprocess.run(
            ["python3", str(SCRIPT), str(FIXTURES / "extracted-stories-sample.json")],
            capture_output=True, text=True,
        )
        import re
        story_ids = re.findall(r"## STORY-(\d+)", result.stdout)
        self.assertEqual(story_ids, ["0001", "0002", "0003", "0004", "0005"])

    def test_no_input_returns_error(self):
        result = subprocess.run(
            ["python3", str(SCRIPT)],
            capture_output=True, text=True,
        )
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest tests.test_aggregate_stories -v`
Expected: FAIL with `AssertionError: ... aggregate_stories.py does not exist`

- [ ] **Step 3: Implement the aggregation script**

Create `scripts/aggregate_stories.py`:

```python
#!/usr/bin/env python3
"""Aggregate extracted story card JSONs into a requirements-index.md.

Usage: aggregate_stories.py <json-file>...

Takes one or more JSON files (each a list of story objects or {"stories": [...]}),
deduplicates by title, groups into epics by epic_theme, assigns stable IDs
(STORY-NNNN, EPIC-NNN), and outputs requirements-index.md to stdout.
"""
import json
import sys
from collections import OrderedDict
from pathlib import Path


def load_stories(paths: list[Path]) -> list[dict]:
    """Load and combine stories from multiple JSON files."""
    all_stories: list[dict] = []
    for p in paths:
        data = json.loads(p.read_text())
        if isinstance(data, list):
            all_stories.extend(data)
        elif isinstance(data, dict) and "stories" in data:
            all_stories.extend(data["stories"])
        else:
            print(f"warning: {p} has unexpected format, skipping", file=sys.stderr)
    return all_stories


def dedup_stories(stories: list[dict]) -> list[dict]:
    """Deduplicate stories by exact title match. Merges sources from duplicates."""
    seen: dict[str, dict] = OrderedDict()
    for story in stories:
        title = story.get("title", "").strip()
        if title in seen:
            existing_sources = seen[title].get("sources", [])
            for src in story.get("sources", []):
                if src not in existing_sources:
                    existing_sources.append(src)
            seen[title]["sources"] = existing_sources
        else:
            seen[title] = dict(story)  # copy to avoid mutating input
    return list(seen.values())


def group_into_epics(stories: list[dict]) -> dict[str, list[dict]]:
    """Group stories by epic_theme. Returns ordered dict {theme: [stories]}."""
    epics: dict[str, list[dict]] = OrderedDict()
    for story in stories:
        theme = story.get("epic_theme", "Uncategorized").strip()
        if theme not in epics:
            epics[theme] = []
        epics[theme].append(story)
    return epics


def format_requirements_index(epics: dict[str, list[dict]]) -> str:
    """Format epics and stories as requirements-index.md content."""
    lines: list[str] = ["# Requirements Index", ""]

    story_counter = 1
    epic_counter = 1

    # First pass: assign IDs and write epic headers
    for theme, stories in epics.items():
        epic_id = f"EPIC-{epic_counter:03d}"
        epic_counter += 1

        story_ids: list[str] = []
        for story in stories:
            sid = f"STORY-{story_counter:04d}"
            story["_id"] = sid
            story["_epic_id"] = epic_id
            story["_epic_theme"] = theme
            story_ids.append(sid)
            story_counter += 1

        primary_sources: set[str] = set()
        for s in stories:
            for src in s.get("sources", []):
                if isinstance(src, dict):
                    primary_sources.add(src.get("file", ""))
                elif isinstance(src, str):
                    primary_sources.add(src)

        lines.append(f"## {epic_id} — {theme}")
        lines.append("")
        lines.append(f"**Summary:** {theme}")
        lines.append(f"**Stories:** {', '.join(story_ids)}")
        if primary_sources:
            sources_str = ", ".join(f"`{s}`" for s in sorted(primary_sources) if s)
            lines.append(f"**Primary sources:** {sources_str}")
        lines.append(f"**Status:** 0/{len(stories)} done")
        lines.append("")

    # Second pass: write story cards
    for theme, stories in epics.items():
        for story in stories:
            sid = story["_id"]
            epic_id = story["_epic_id"]
            epic_theme = story["_epic_theme"]

            lines.append(f"## {sid}")
            lines.append("")
            lines.append(f"**Epic:** {epic_id} — {epic_theme}")
            lines.append(f"**Title:** {story.get('title', 'Untitled')}")
            lines.append("")
            lines.append(f"**As a** {story.get('as_a', 'user')}")
            lines.append(f"**I want** {story.get('i_want', 'this feature')}")
            lines.append(f"**So that** {story.get('so_that', 'I can benefit')}")
            lines.append("")
            lines.append("**Acceptance criteria:**")
            for ac in story.get("acceptance_criteria", []):
                lines.append(f"- {ac}")
            lines.append("")
            lines.append("**Sources:**")
            for src in story.get("sources", []):
                if isinstance(src, dict):
                    file_ref = src.get("file", "unknown")
                    line_ref = src.get("lines", "")
                    ref = f"`{file_ref}:{line_ref}`" if line_ref else f"`{file_ref}`"
                    lines.append(f"- {ref}")
                elif isinstance(src, str):
                    lines.append(f"- `{src}`")
            lines.append("")
            lines.append("**Status:** pending")
            lines.append("")

    return "\n".join(lines)


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: aggregate_stories.py <json-file>...", file=sys.stderr)
        return 2

    paths = [Path(p) for p in sys.argv[1:]]
    for p in paths:
        if not p.exists():
            print(f"error: file not found: {p}", file=sys.stderr)
            return 2

    stories = load_stories(paths)
    if not stories:
        print("error: no stories found in input files", file=sys.stderr)
        return 1

    deduped = dedup_stories(stories)
    epics = group_into_epics(deduped)
    output = format_requirements_index(epics)
    print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

Make it executable:
```bash
chmod +x scripts/aggregate_stories.py
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest tests.test_aggregate_stories -v`
Expected: PASS, all 6 tests pass

Also verify no regressions: `python3 -m unittest discover tests/ -v`
Expected: all tests pass (Plan 1 tests + chunking tests + aggregation tests)

- [ ] **Step 5: Commit**

```bash
git add scripts/aggregate_stories.py tests/test_aggregate_stories.py
git commit -m "feat: add aggregate_stories.py for story dedup and ID assignment"
```

---

### Task 6: Pipeline integration test

**Files:**
- Create: `tests/test_extraction_pipeline.py`

This test verifies the full pipeline: chunk a multi-file spec → use the sample extracted stories → aggregate → validate the output as a valid requirements-index.md.

- [ ] **Step 1: Write the integration test**

Create `tests/test_extraction_pipeline.py`:

```python
"""Integration test for the extraction pipeline.

Tests: chunk multi-file spec → [sample extraction output] → aggregate → validate.
The extraction step (LLM dispatch) is replaced by a pre-extracted fixture.
"""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).parent.parent / "scripts"
FIXTURES = Path(__file__).parent / "fixtures"


class TestExtractionPipeline(unittest.TestCase):
    def test_chunk_then_aggregate_produces_valid_index(self):
        """Full pipeline: chunk the multi-file spec, aggregate the sample output, validate."""
        # Step 1: Chunk the multi-file spec (verifies chunking works on fixture)
        chunk_result = subprocess.run(
            ["python3", str(SCRIPTS / "chunk_spec.py"),
             str(FIXTURES / "multi-file-spec")],
            capture_output=True, text=True,
        )
        self.assertEqual(chunk_result.returncode, 0, msg=chunk_result.stderr)
        chunks = json.loads(chunk_result.stdout)
        self.assertGreaterEqual(len(chunks), 3, "Expected at least 3 chunks from 3 files")

        # Step 2: Aggregate the sample extraction output (simulates what subagents return)
        agg_result = subprocess.run(
            ["python3", str(SCRIPTS / "aggregate_stories.py"),
             str(FIXTURES / "extracted-stories-sample.json")],
            capture_output=True, text=True,
        )
        self.assertEqual(agg_result.returncode, 0, msg=agg_result.stderr)

        # Step 3: Validate the aggregated output
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
            f.write(agg_result.stdout)
            tmp = f.name
        try:
            val_result = subprocess.run(
                ["python3", str(SCRIPTS / "validate_artifact.py"),
                 "--type", "requirements-index", tmp],
                capture_output=True, text=True,
            )
            self.assertEqual(val_result.returncode, 0,
                             msg=f"Validator failed on aggregated output: {val_result.stderr}")
        finally:
            Path(tmp).unlink()

    def test_aggregated_output_has_correct_story_count(self):
        """Sample fixture has 5 stories — aggregation should produce 5 STORY headers."""
        result = subprocess.run(
            ["python3", str(SCRIPTS / "aggregate_stories.py"),
             str(FIXTURES / "extracted-stories-sample.json")],
            capture_output=True, text=True,
        )
        import re
        story_count = len(re.findall(r"^## STORY-\d+$", result.stdout, re.MULTILINE))
        self.assertEqual(story_count, 5, f"Expected 5 stories, got {story_count}")

    def test_aggregated_output_has_correct_epic_count(self):
        """Sample fixture has 2 epic themes — aggregation should produce 2 EPIC headers."""
        result = subprocess.run(
            ["python3", str(SCRIPTS / "aggregate_stories.py"),
             str(FIXTURES / "extracted-stories-sample.json")],
            capture_output=True, text=True,
        )
        import re
        epic_count = len(re.findall(r"^## EPIC-\d+", result.stdout, re.MULTILINE))
        self.assertEqual(epic_count, 2, f"Expected 2 epics, got {epic_count}")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they pass**

Run: `python3 -m unittest tests.test_extraction_pipeline -v`
Expected: PASS, all 3 tests pass

Full suite: `python3 -m unittest discover tests/ -v`
Expected: all tests pass

- [ ] **Step 3: Commit**

```bash
git add tests/test_extraction_pipeline.py
git commit -m "test: add extraction pipeline integration test"
```

---

### Task 7: Update extracting-requirements SKILL.md

**Files:**
- Modify: `skills/extracting-requirements/SKILL.md`

Replace the walking-skeleton behavior with the full extraction pipeline.

- [ ] **Step 1: Rewrite SKILL.md**

Replace the entire contents of `skills/extracting-requirements/SKILL.md` with:

```markdown
---
name: extracting-requirements
description: Use when starting an iterative-development run on human spec collateral — reads the spec, produces a structured requirements-index.md containing story cards and epics with stable IDs.
---

# Extracting Requirements

## Overview

Reads arbitrary human spec collateral (one file, a directory, or a large prose dump) and produces `docs/superpowers/iterations/requirements-index.md` — the plugin's internal backlog of story cards and epics with stable global IDs.

Uses a chunking + parallel-dispatch + aggregation pipeline so that no single agent holds the entire spec in context. Handles specs from a single page up to ~100K tokens across dozens of files.

## When to Use

Invoked by `iterative-development` during bootstrap, or standalone when you need to regenerate the requirements index from human spec collateral.

## Pipeline

### 1. Inventory

Enumerate the spec files without reading full contents:

```bash
python3 scripts/chunk_spec.py <spec-path>
```

This produces a JSON array of chunks. Each chunk has `source_file`, `heading`, `start_line`, `end_line`, `content`, and `estimated_tokens`. Small files (< 4K tokens) are kept whole. Larger files are split by `##` headings, or `###` if sections are still too large.

### 2. Dispatch extraction subagents

For each chunk (or batch of small chunks), dispatch an extraction subagent using the template in `extraction-subagent-prompt.md`. Pass the chunk content inline — do NOT make the subagent read the file.

**Dispatch strategy:**
- Dispatch subagents in parallel where possible (use the Agent tool with multiple parallel calls)
- Main agent chooses parallelism based on chunk count and judgment
- Each subagent returns a JSON object with a `stories` array
- Save each subagent's output to a temp JSON file

### 3. Aggregate

Run the aggregation script on all extracted story JSONs:

```bash
python3 scripts/aggregate_stories.py <json-file-1> <json-file-2> ... > docs/superpowers/iterations/requirements-index.md
```

The script:
- Combines all stories from all input files
- Deduplicates by exact title match (merges sources)
- Groups stories into epics by `epic_theme`
- Assigns stable IDs: STORY-0001..STORY-NNNN, EPIC-001..EPIC-NNN
- Outputs formatted `requirements-index.md`

### 4. Validate

```bash
python3 scripts/validate_artifact.py --type requirements-index docs/superpowers/iterations/requirements-index.md
```

If validation fails, inspect the output, fix formatting issues, and re-validate.

### 5. Commit

```bash
git add docs/superpowers/iterations/requirements-index.md
git commit -m "docs: add requirements-index.md extracted from spec"
```

## Quick Reference

| Step | Tool | Input | Output |
|---|---|---|---|
| Chunk | `scripts/chunk_spec.py` | spec path | JSON chunks (stdout) |
| Extract | Agent tool + `extraction-subagent-prompt.md` | chunk content | JSON stories (per subagent) |
| Aggregate | `scripts/aggregate_stories.py` | JSON files | `requirements-index.md` (stdout) |
| Validate | `scripts/validate_artifact.py --type requirements-index` | .md file | OK or errors |

## Deferred to later plans

Hierarchical reduce (specs > 1M tokens where single aggregation exceeds context), huge-spec decomposition (sub-project identification before chunking), incremental re-extraction (new spec files mid-project).
```

- [ ] **Step 2: Validate the updated SKILL.md**

Run: `python3 scripts/validate_skill.py skills/extracting-requirements/SKILL.md`
Expected: `OK: skills/extracting-requirements/SKILL.md` (word count warning acceptable)

- [ ] **Step 3: Commit**

```bash
git add skills/extracting-requirements/SKILL.md
git commit -m "feat: update extracting-requirements with chunking + parallel + aggregation pipeline"
```

---

### Task 8: Update validation suite

**Files:**
- Modify: `scripts/run_validation_suite.sh`

Add the new test files to the suite runner so it exercises the full Plan 2 code.

- [ ] **Step 1: Update run_validation_suite.sh**

Replace the entire contents of `scripts/run_validation_suite.sh` with:

```bash
#!/usr/bin/env bash
# Validation suite for the iterative-development plugin.
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
echo "=== Verifying extraction pipeline scripts ==="
python3 scripts/chunk_spec.py tests/fixtures/multi-file-spec/ > /dev/null
echo "OK: chunk_spec.py runs on multi-file-spec fixture"
python3 scripts/aggregate_stories.py tests/fixtures/extracted-stories-sample.json > /dev/null
echo "OK: aggregate_stories.py runs on sample fixture"

echo ""
echo "=== All validation checks passed ==="
```

- [ ] **Step 2: Run the full suite**

Run: `bash scripts/run_validation_suite.sh`
Expected: all checks pass, ends with `=== All validation checks passed ===`

- [ ] **Step 3: Commit**

```bash
git add scripts/run_validation_suite.sh
git commit -m "chore: update validation suite with extraction pipeline checks"
```

---

## Plan Completion Checklist

After all 8 tasks are complete, verify:

- [ ] `bash scripts/run_validation_suite.sh` exits with code 0
- [ ] `python3 scripts/chunk_spec.py tests/fixtures/multi-file-spec/` produces 3 chunks from 3 files
- [ ] `python3 scripts/aggregate_stories.py tests/fixtures/extracted-stories-sample.json` produces valid `requirements-index.md` (pipe to validator to confirm)
- [ ] `extracting-requirements` SKILL.md describes the full pipeline (chunk → dispatch → aggregate → validate)
- [ ] Extraction subagent prompt template exists and describes JSON output format
- [ ] All unit tests pass with no regressions from Plan 1
- [ ] Git history shows 8 new commits (one per task)

**Deferred to later plans (do NOT attempt in Plan 2):**
- Hierarchical reduce (multi-tier aggregation for >1M token specs)
- Huge-spec decomposition (sub-project identification)
- Incremental re-extraction (new spec files mid-project)
- Parallel adversarial review on extraction (Plan 3)

**Next plan:** Plan 3 — Parallel Adversarial Review (PAR) everywhere.
