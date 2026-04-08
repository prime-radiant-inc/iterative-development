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

## Script Location

All scripts referenced below live in this skill's `scripts/` directory, next to this SKILL.md file.

## Pipeline

### 1. Inventory

Enumerate the spec files without reading full contents:

```bash
python3 "scripts/chunk_spec.py" <spec-path>
```

This produces a JSON array of chunks. Each chunk has `source_file`, `heading`, `start_line`, `end_line`, `content`, and `estimated_tokens`. Small files (< 4K tokens) are kept whole. Larger files are split by `##` headings, or `###` if sections are still too large.

### 2. Dispatch extraction subagents

For each chunk (or batch of small chunks), dispatch an extraction subagent using the template in `extraction-subagent-prompt.md`. Pass the chunk content inline — do NOT make the subagent read the file.

**Dispatch strategy:**
- Dispatch subagents in parallel, but respect runtime thread limits (typically 3-6 concurrent agents). Batch chunks into waves if the chunk count exceeds the limit.
- Each subagent returns a JSON object with a `stories` array
- Save each subagent's output to a temp JSON file
- **Track completion:** record which chunks were dispatched and which returned successfully. If any subagent fails or times out, re-dispatch that chunk before proceeding to aggregation.

### 3. Aggregate

Run the aggregation script on all extracted story JSONs:

```bash
python3 "scripts/aggregate_stories.py" <json-file-1> <json-file-2> ... > docs/superpowers/iterations/requirements-index.md
```

The script:
- Combines all stories from all input files
- Deduplicates by exact title match (merges sources)
- Groups stories into epics by `epic_theme`
- Assigns stable IDs: STORY-0001..STORY-NNNN, EPIC-001..EPIC-NNN
- Outputs formatted `requirements-index.md`

### 4. Consolidate epics

The aggregation script groups by exact `epic_theme` string. Since extraction subagents work independently, they often name the same domain differently — producing duplicate or near-duplicate epics.

After aggregation, review the epic list and consolidate:

1. Extract the epic names: `grep "^## EPIC-" docs/superpowers/iterations/requirements-index.md`
2. Identify groups that should merge:
   - "Parent - Child" variants (e.g., "Recording Pipeline - State Machine" → "Recording Pipeline")
   - Near-synonyms (e.g., "Audio Capture" + "Audio Capture and Encoding" + "Audio Recording")
   - Same domain from different spec angles (e.g., "Privacy Permissions" + "Permissions")
   - Keep epics separate when they represent genuinely different concerns
3. For each merge: update the `epic_theme` in the extracted JSON files to use the canonical name
4. Re-run the aggregation script to produce the consolidated index
5. Verify the epic count is reasonable (roughly 20-40 for a large project, fewer for smaller ones)

**Do NOT merge epics that are legitimately different.** "Keyboard Input" (raw event handling) and "Keyboard Shortcuts" (user-configurable bindings) are separate concerns even though both say "Keyboard." Use domain judgment.

### 5. Coverage verification

After aggregation and consolidation, verify extraction coverage:

1. List every spec file and its `##` headings (from the chunk inventory in step 1)
2. For each spec section, check that at least one story in the requirements index cites that source file
3. Flag any spec file or major section with zero story coverage — these are gaps in extraction
4. If gaps exist: re-run extraction subagents on the uncovered chunks and re-aggregate

This step catches silent under-scoping — the most dangerous failure mode is an extraction that looks complete but missed entire spec surfaces.

**Derivative artifacts warning:** if the spec directory contains both canonical documents (e.g., domain specs, journey specs) and derivative summaries (e.g., acceptance-criteria rollups, audit reports), always extract from the canonical documents. Derivative artifacts may collapse or omit detail. If you use derivatives as a convenience, verify their coverage against the canonical source list.

### 6. Validate

```bash
python3 "scripts/validate_requirements_index.py" docs/superpowers/iterations/requirements-index.md
```

If validation fails, inspect the output, fix formatting issues, and re-validate.

### 7. Commit

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
| Consolidate | Agent review of epic list | epic names | Normalized themes → re-aggregate |
| Coverage check | Compare chunk inventory → story sources | chunk list, stories | Uncovered spec sections |
| Validate | `scripts/validate_requirements_index.py` | .md file | OK or errors |

## Deferred to later plans

Hierarchical reduce (specs > 1M tokens where single aggregation exceeds context), huge-spec decomposition (sub-project identification before chunking), incremental re-extraction (new spec files mid-project).
