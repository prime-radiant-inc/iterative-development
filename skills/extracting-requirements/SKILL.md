---
name: extracting-requirements
description: Use when starting an iterative-development run on human spec collateral — reads the spec, produces per-epic requirement files with proof obligations and behavior scenario cards with stable IDs.
---

# Extracting Requirements

## Overview

Reads arbitrary human spec collateral and produces two artifact sets:
1. **Per-epic requirement files** in `docs/superpowers/iterations/requirements/` — story cards with proof obligations per AC
2. **Behavior scenarios** in `docs/superpowers/iterations/behavior-scenarios.md` — reusable observable-behavior contracts with stable IDs

Uses a chunking + parallel-dispatch + aggregation pipeline so that no single agent holds the entire spec in context. Handles specs from a single page up to ~100K tokens across dozens of files.

## When to Use

Invoked by `iterative-development` during bootstrap, or standalone when you need to regenerate requirements from human spec collateral.

## Script Location

All scripts referenced below live in this skill's `scripts/` directory, next to this SKILL.md file.

## Key Concept: Spec Taxonomy

The spec directory structure drives proof seam classification. See `skills/shared/behavior-evidence-formats.md` for the full taxonomy. Summary:

| Spec directory | Default proof seam |
|---|---|
| `test-vectors/` | unit |
| `contracts/` | integration |
| `domains/` | integration or app-level |
| `journeys/` | e2e |

Extraction subagents use the appropriate prompt variant based on source file location.

## Pipeline

### 1. Inventory

Enumerate the spec files without reading full contents:

```bash
python3 "scripts/chunk_spec.py" <spec-path>
```

This produces a JSON array of chunks. Each chunk has `source_file`, `heading`, `start_line`, `end_line`, `content`, and `estimated_tokens`. Small files (< 4K tokens) are kept whole. Larger files are split by `##` headings, or `###` if sections are still too large.

**Classify each chunk by spec taxonomy:** note whether the source file is under `journeys/`, `contracts/`, `domains/`, or `test-vectors/`. This determines which extraction prompt variant to use.

### 2. Dispatch extraction subagents

For each chunk (or batch of small chunks), dispatch an extraction subagent using the appropriate template from `extraction-subagent-prompt.md`:

- Chunks from `journeys/` → use the **Journey Extraction** prompt variant
- All other chunks → use the **Standard Extraction** prompt variant

Pass the chunk content inline — do NOT make the subagent read the file.

**Dispatch strategy:**
- Dispatch subagents in waves of 3-5 (runtime agent thread limits are typically 6; keep headroom). Do not fan out all chunks at once.
- **Persist immediately:** as soon as each subagent returns, write its output to a temp file (e.g., `.codex-temp/extraction/raw/batch-NN.json` or equivalent) before dispatching more work. Subagent results that only exist in conversation state can be lost if the session fails.
- **Wait semantics:** if your runtime's wait primitive returns on the first completed agent (not all), loop until every dispatched agent in the wave has reached a final state. Persist each result as it arrives.
- Close completed agents promptly to free thread slots for the next wave.
- **Track completion:** maintain a checklist of chunk-to-agent mappings. After all waves finish, verify every chunk produced a persisted output file. Re-dispatch any missing chunks before proceeding.

### 3. PAR omission review

Before aggregation, run a PAR omission review. The sole job of this review is to find requirements AND scenarios that the extraction subagents dropped.

For each chunk (or batch of chunks), dispatch two reviewers in parallel following `skills/shared/parallel-adversarial-review.md`:

1. Give each reviewer the **original chunk text** and the **extracted stories + scenarios** for that chunk
2. Prompt: "Compare the source text against the extracted stories and scenarios. Find every requirement, acceptance criterion, behavioral constraint, or observable behavior in the source that is NOT represented by any extracted story or scenario. Score 5 points for each omission found. Pay special attention to: (a) ACs missing proof obligations, (b) observable behavior with no scenario, (c) journey steps that were summarized or skipped."
3. Aggregate findings across both reviewers
4. For each confirmed omission: either add a new story/scenario to the extraction output or document why it's intentionally excluded

This pass is required, not optional. Extraction subagents optimize for what they notice; omission reviewers optimize for what's missing.

### 4. Aggregate stories

Run the story aggregation script on all extracted story JSONs (including any added by the omission review):

```bash
python3 "scripts/aggregate_stories.py" -o docs/superpowers/iterations/requirements/ <json-file-1> <json-file-2> ...
```

The script combines, deduplicates by title, groups into epics, assigns stable STORY/EPIC IDs, and outputs per-epic files with proof obligations preserved.

### 5. Aggregate scenarios

Run the scenario aggregation script:

```bash
python3 "scripts/aggregate_scenarios.py" \
  -o docs/superpowers/iterations/behavior-scenarios.md \
  --stories-dir docs/superpowers/iterations/requirements/ \
  <json-file-1> <json-file-2> ...
```

The script combines, deduplicates by title, assigns stable SCENARIO/JOURNEY IDs, resolves story title references to STORY-IDs, and outputs `behavior-scenarios.md`.

### 6. Consolidate epics

Same as before: review the epic list, merge near-duplicates, re-run aggregation. See the consolidation rules in the original extraction skill documentation.

**Additional consolidation check:** after merging, verify that scenario `owning_story_titles` still resolve correctly. If stories were deduplicated during re-aggregation, re-run scenario aggregation to update resolved refs.

### 7. Back-link scenarios to stories

After both aggregations complete, run the back-linking script to update per-epic story files with scenario references:

```bash
python3 "scripts/backlink_scenarios.py" \
  docs/superpowers/iterations/behavior-scenarios.md \
  docs/superpowers/iterations/requirements/
```

The script reads scenario → owning-story mappings from `behavior-scenarios.md` and appends `scenario:SCENARIO-NNNN` or `scenario:JOURNEY-NNNN` to AC lines in the epic files that have observable behavioral impact. AC lines that already have scenario refs are skipped.

This creates the bidirectional link: stories → scenarios (via AC lines) and scenarios → stories (via owning_stories field).

### 8. Coverage ledger

Build a coverage ledger that maps every spec chunk to its extracted stories AND scenarios. This is the traceable proof that extraction is complete.

For each chunk from the inventory (step 1):

1. List the chunk: `source_file`, `heading`, `start_line`–`end_line`
2. List every story ID whose `**Sources:**` field cites overlapping lines in that file
3. List every scenario ID whose `**Sources:**` field cites overlapping lines in that file
4. Classify the chunk:
   - **covered** — stories with ACs that correspond to normative content AND scenarios for observable behavior
   - **story-only** — stories exist but observable behavior has no scenario (needs scenario)
   - **non-normative** — chunk contains only meta-commentary, table of contents, or boilerplate (explain why)
   - **duplicate** — chunk's requirements are covered by stories citing a different source
   - **gap** — normative content with no corresponding story

**Hard gates:**
- If any chunk is classified as **gap**, extraction is incomplete. Re-extract and repeat.
- If any chunk is classified as **story-only** and contains observable behavior, extraction is incomplete. Add scenarios for the missing observable behavior.

**Journey coverage check:** every journey spec file MUST produce at least one JOURNEY-NNNN scenario that preserves the complete step sequence. If a journey file only produced stories (no journey scenario), that is a gap.

### 9. Initialize behavior corpus index

Create the initial `docs/superpowers/iterations/behavior-corpus.md` from the scenario list:

```markdown
# Behavior Corpus

| Scenario ID | Title | Proof seam | Run cadence | Command | Owning stories |
|---|---|---|---|---|---|
```

Populate with all scenarios. Set run cadence:
- Journey scenarios → `sentinel` (they run every iteration)
- Surface scenarios → `iteration` (default, refined during scoping)

Set command to `TBD` — the implementing iterations will fill these in.

### 10. Validate

```bash
python3 "scripts/validate_requirements_index.py" docs/superpowers/iterations/requirements/
python3 "scripts/validate_scenarios.py" docs/superpowers/iterations/behavior-scenarios.md docs/superpowers/iterations/requirements/
```

If validation fails, inspect the output, fix formatting issues, and re-validate.

### 11. Commit

```bash
git add docs/superpowers/iterations/requirements/
git add docs/superpowers/iterations/behavior-scenarios.md
git add docs/superpowers/iterations/behavior-corpus.md
git commit -m "docs: add requirements with proof obligations, behavior scenarios, and corpus index"
```

## Quick Reference

| Step | Tool | Input | Output |
|---|---|---|---|
| Chunk | `scripts/chunk_spec.py` | spec path | JSON chunks (stdout) |
| Extract | Agent tool + `extraction-subagent-prompt.md` | chunk content | JSON stories + scenarios (per subagent) |
| Omission review | PAR (source text vs. stories + scenarios) | chunks + stories + scenarios | Missing requirements and scenarios |
| Aggregate stories | `scripts/aggregate_stories.py -o <dir>` | JSON files | Per-epic .md files with proof obligations |
| Aggregate scenarios | `scripts/aggregate_scenarios.py -o <file>` | JSON files + stories dir | `behavior-scenarios.md` |
| Back-link | `scripts/backlink_scenarios.py` | scenarios + stories | Updated AC lines with scenario refs |
| Coverage ledger | Map chunks → story IDs + scenario IDs | chunk list, stories, scenarios | Gap/covered/story-only per chunk |
| Init corpus | Write corpus index | scenario list | `behavior-corpus.md` |
| Validate | `scripts/validate_requirements_index.py` + `scripts/validate_scenarios.py` | .md files | OK or errors |

## Deferred to later plans

Hierarchical reduce (specs > 1M tokens), huge-spec decomposition, incremental re-extraction.
