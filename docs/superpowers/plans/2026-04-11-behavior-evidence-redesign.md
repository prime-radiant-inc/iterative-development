# Behavior Evidence Redesign — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Redesign the iterative-development skills so they continuously build and maintain a reusable black-box behavior corpus alongside the code, proving real behavior at the correct seam — not just that stories are implemented.

**Architecture:** Three new artifact types (scenario cards, proof obligations per AC, behavior corpus index) flow through all 6 skills. Extraction emits scenarios alongside stories. The spec taxonomy (journeys → E2E, domains → integration, contracts → integration, test-vectors → unit) drives proof seam classification. Audits verify evidence quality in three tiers (deep + impacted + sentinel). The orchestrator's completion gate shifts from "stories done" to "behavior evidence passes."

**Tech Stack:** Markdown skill files, markdown prompt templates, Python validation scripts, git

---

## File Structure

### Files to Create

| File | Purpose |
|---|---|
| `skills/shared/behavior-evidence-formats.md` | Reference doc: scenario card format, proof obligation format, behavior corpus format |
| `skills/extracting-requirements/scripts/aggregate_scenarios.py` | Aggregate extracted scenario JSONs into `behavior-scenarios.md` |
| `skills/extracting-requirements/scripts/validate_scenarios.py` | Validate scenario format, cross-check story refs |

### Files to Modify

| File | Nature of change |
|---|---|
| `skills/extracting-requirements/extraction-subagent-prompt.md` | Add scenario + proof obligation extraction to JSON output |
| `skills/extracting-requirements/scripts/aggregate_stories.py` | Extend story format with proof obligations |
| `skills/extracting-requirements/SKILL.md` | Add scenario extraction pipeline steps, extend coverage ledger |
| `skills/scoping-the-simplest-core/SKILL.md` | Add story splitting rule, walking skeleton scenario requirements |
| `skills/running-an-iteration/scope-reviewer-prompt.md` | Add scenario coverage check |
| `skills/running-an-iteration/SKILL.md` | Add evidence tasks, sentinel corpus runs |
| `skills/implementing-tasks/implementer-subagent-prompt.md` | Add AC → proof seam pre-flight mapping |
| `skills/implementing-tasks/spec-compliance-reviewer-prompt.md` | Add evidence quality check |
| `skills/implementing-tasks/code-quality-reviewer-prompt.md` | Add corpus contribution inspection |
| `skills/implementing-tasks/SKILL.md` | Add evidence task framing |
| `skills/auditing-progress/auditor-subagent-prompt.md` | Rewrite for three-tier behavior evidence audit |
| `skills/auditing-progress/SKILL.md` | Replace two-tier with three-tier, add sentinel corpus |
| `skills/iterative-development/SKILL.md` | Shift completion gate to behavior evidence |

---

## Task 1: Define behavior evidence artifact formats

**Files:**
- Create: `skills/shared/behavior-evidence-formats.md`

This reference document defines the formats that all skills consume and produce. Every downstream task depends on these formats being defined first.

- [ ] **Step 1: Write the behavior evidence formats reference**

Write `skills/shared/behavior-evidence-formats.md`:

```markdown
# Behavior Evidence Formats

Shared reference for all iterative-development skills. Defines the artifact formats for behavior evidence.

## Spec Taxonomy → Proof Seam

The spec directory structure drives proof seam classification:

| Spec directory | Content type | Default proof seam |
|---|---|---|
| `test-vectors/` | Input/output pairs for parsers, codecs, formatters | unit |
| `contracts/` | Integration boundaries (third-party SDKs, OS APIs) | integration |
| `domains/` | Internal subsystem behavior | integration or app-level |
| `journeys/` | Complete user flows across subsystems | e2e |

Extractors use this mapping when assigning proof obligations to ACs. The default can be overridden per AC when the content justifies a different seam — but the override must be justified in the proof obligation.

## Proof Seam Levels

| Seam | Meaning | Example |
|---|---|---|
| `unit` | In-process, single-module, no I/O | Parser, formatter, state machine |
| `integration` | Multi-module or real I/O, still in-process | Persistence contract, SDK integration |
| `app-level` | App launched, observed via AX/window/menu inspection | Menu action, window lifecycle, permission prompt |
| `process-level` | Spawns or observes external processes | Relaunch, update install, CLI tool |
| `e2e` | Full assembled product path with real inputs | User journey: hotkey → record → transcribe → paste |

## Story Card Format (Extended)

Standard story card fields plus:

```
**Acceptance criteria:**
- AC-1: [text] · impact:`local` · seam:`integration` · scenario:`SCENARIO-NNNN`
- AC-2: [text] · impact:`none` · seam:`unit`
- AC-3: [text] · impact:`journey` · seam:`e2e` · scenario:`SCENARIO-NNNN`
```

Proof obligation fields appended to each AC line:
- `impact:` — `none` | `local` | `cross-surface` | `journey`
  - `none`: internal implementation detail, no externally observable effect
  - `local`: observable on one surface (a single UI element, a single API response)
  - `cross-surface`: observable across multiple surfaces (settings change affects recording)
  - `journey`: observable only in an assembled multi-step flow
- `seam:` — proof seam level from the table above
- `scenario:` — scenario ID reference (omit for `impact:none`)

If `impact` is anything other than `none`, a `seam` and `scenario` ref are required.

## Scenario Card Format

Scenarios live in `docs/superpowers/iterations/behavior-scenarios.md`. Two kinds: surface and journey.

### Surface Scenario

```markdown
## SCENARIO-NNNN — [title]

**Kind:** surface | failure-recovery | contract
**Proof seam:** [seam level]
**Owning stories:** STORY-NNNN, STORY-NNNN

**Preconditions:**
- [condition]

**Action:**
- [what happens]

**Expected observables:**
- [what must be true after the action]

**Automation status:** automated | manual-residual
**Execution command:** `[command]` (if automated)
**Manual residual:** [what can't be automated and why] (if manual-residual)

**Sources:**
- `[spec file:lines]`
```

### Journey Scenario Chain

Journey scenarios preserve the step sequence from the spec. They are ordered chains, not independent checks.

```markdown
## JOURNEY-NNNN — [title]

**Journey:** [journey ID from spec, e.g., J-NORMAL-DICTATION]
**Proof seam:** e2e
**Owning stories:** STORY-NNNN, STORY-NNNN, ...

**Preconditions:**
- [condition]

**Steps:**
1. [actor action or system event]
   → [expected observable]
2. [next action]
   → [expected observable]
   → [expected observable]
...

**Final observables:**
- [what must be true when the journey completes]

**Automation status:** automated | manual-residual
**Execution command:** `[command]` (if automated)
**Manual residual:** [what can't be automated and why] (if manual-residual)

**Sources:**
- `[spec file:lines]`
```

## Behavior Corpus Index

Lives in `docs/superpowers/iterations/behavior-corpus.md`. Lightweight table for auditors and the orchestrator.

```markdown
# Behavior Corpus

| Scenario ID | Title | Proof seam | Run cadence | Command | Owning stories |
|---|---|---|---|---|---|
| SCENARIO-0001 | ... | integration | iteration | `scripts/...` | STORY-0001 |
| JOURNEY-0001 | ... | e2e | sentinel | `scripts/...` | STORY-0005, STORY-0010 |
```

Run cadence values:
- `task` — run after the implementing task that changes this scenario's surface
- `iteration` — run at iteration wrap-up
- `sentinel` — run every iteration regardless of what changed (high-value regression guard)

## Extraction JSON Format (Extended)

Extraction subagents produce:

```json
{
  "stories": [
    {
      "title": "...",
      "epic_theme": "...",
      "as_a": "...",
      "i_want": "...",
      "so_that": "...",
      "acceptance_criteria": [
        {
          "id": "AC-1",
          "text": "...",
          "behavioral_impact": "none|local|cross-surface|journey",
          "proof_seam": "unit|integration|app-level|process-level|e2e"
        }
      ],
      "sources": [{"file": "...", "lines": "..."}]
    }
  ],
  "scenarios": [
    {
      "title": "...",
      "kind": "surface|journey|failure-recovery|contract",
      "proof_seam": "unit|integration|app-level|process-level|e2e",
      "preconditions": ["..."],
      "steps": [
        {"action": "...", "expected": ["..."]}
      ],
      "final_observables": ["..."],
      "owning_story_titles": ["..."],
      "sources": [{"file": "...", "lines": "..."}]
    }
  ]
}
```

For journey scenarios, `steps` is the ordered sequence. For surface scenarios, `steps` has one entry (the action + observables).
```

- [ ] **Step 2: Commit**

```bash
git add skills/shared/behavior-evidence-formats.md
git commit -m "docs: add behavior evidence artifact format reference"
```

---

## Task 2: Extend extraction subagent prompt for scenarios and proof obligations

**Files:**
- Modify: `skills/extracting-requirements/extraction-subagent-prompt.md`

The extraction subagent now produces both stories (with proof obligations per AC) and scenarios (surface or journey) in one pass.

- [ ] **Step 1: Rewrite the extraction subagent prompt**

Replace the full content of `skills/extracting-requirements/extraction-subagent-prompt.md` with:

```markdown
# Extraction Subagent Prompt Template

Use this template when dispatching an extraction subagent. Fill in the bracketed values.

The spec taxonomy drives proof seam defaults:
- Source in `test-vectors/` → default seam `unit`
- Source in `contracts/` → default seam `integration`
- Source in `domains/` → default seam `integration` (upgrade to `app-level` if AC describes user-visible behavior)
- Source in `journeys/` → default seam `e2e`

## Standard Extraction (domains, contracts, test-vectors)

~~~
Agent tool (general-purpose):
  description: "Extract stories + scenarios from [source description]"
  prompt: |
    You are extracting testable requirements and behavior scenarios from spec documentation.

    ## Your Input

    The following spec content is from [source_file] (lines [start_line]-[end_line]):

    ---
    [chunk content pasted here]
    ---

    ## Your Job

    Read the spec content and produce TWO outputs: story cards and scenario cards.

    ### Output Format

    Produce this EXACT JSON structure:

    {
      "stories": [
        {
          "title": "Short imperative title",
          "epic_theme": "Domain grouping theme",
          "as_a": "actor role",
          "i_want": "capability",
          "so_that": "benefit",
          "acceptance_criteria": [
            {
              "id": "AC-1",
              "text": "Specific testable criterion with expected behavior",
              "behavioral_impact": "none|local|cross-surface|journey",
              "proof_seam": "unit|integration|app-level|process-level|e2e"
            }
          ],
          "sources": [
            {"file": "[source_file]", "lines": "[relevant line range]"}
          ]
        }
      ],
      "scenarios": [
        {
          "title": "Descriptive scenario title",
          "kind": "surface|failure-recovery|contract",
          "proof_seam": "unit|integration|app-level|process-level|e2e",
          "preconditions": ["precondition 1"],
          "steps": [
            {"action": "what happens", "expected": ["what must be true"]}
          ],
          "final_observables": ["what must be true after the scenario"],
          "owning_story_titles": ["title of story this scenario proves"],
          "sources": [
            {"file": "[source_file]", "lines": "[relevant line range]"}
          ]
        }
      ]
    }

    ### Story Rules

    - Every story MUST have at least one acceptance criterion
    - Each AC MUST include behavioral_impact and proof_seam
    - behavioral_impact: "none" = internal detail; "local" = one surface; "cross-surface" = multiple surfaces; "journey" = multi-step flow
    - proof_seam: the cheapest test level that can falsify the behavior. Defaults: [DEFAULT_SEAM based on source directory]
    - Sources must cite the specific file and line range
    - Do NOT assign STORY-NNNN or EPIC-NNN IDs — the aggregator does that
    - Do NOT attempt deduplication — the aggregator handles that
    - Do NOT invent requirements not present in the spec

    ### Scenario Rules

    - If ANY AC has behavioral_impact other than "none", there MUST be at least one scenario that covers it
    - Scenarios describe observable behavior, not implementation
    - Multiple ACs from different stories can share one scenario
    - One story may need multiple scenarios
    - For failure-recovery scenarios: preconditions include the failure state; action is the recovery; observables are the recovered state
    - proof_seam must match or exceed the highest proof_seam of the ACs it covers
    - owning_story_titles references story titles (not IDs, which don't exist yet)

    ### When to Emit Scenarios

    Emit a scenario when the spec describes behavior that is:
    - Observable by a user, operator, or external system
    - Verifiable by checking state, output, or side effects
    - Not purely internal implementation detail

    Do NOT emit scenarios for:
    - Internal data structures with no external effect
    - Implementation approach choices
    - Non-normative commentary

    Output ONLY the JSON object. No other text, no markdown fences, no explanation.
~~~

## Journey Extraction (journeys/)

For chunks from journey spec files, use this variant instead. Journey specs have a sequential step structure that must be preserved as a journey scenario chain.

~~~
Agent tool (general-purpose):
  description: "Extract stories + journey scenario from [source description]"
  prompt: |
    You are extracting testable requirements and a journey scenario chain
    from a user journey spec.

    ## Your Input

    The following journey spec is from [source_file] (lines [start_line]-[end_line]):

    ---
    [chunk content pasted here]
    ---

    ## Your Job

    This is a USER JOURNEY — a sequential multi-step flow. Produce:
    1. Story cards for each implementable responsibility
    2. ONE journey scenario chain that preserves the complete step sequence

    ### Output Format

    {
      "stories": [
        {
          "title": "Short imperative title",
          "epic_theme": "Domain grouping theme",
          "as_a": "actor role",
          "i_want": "capability",
          "so_that": "benefit",
          "acceptance_criteria": [
            {
              "id": "AC-1",
              "text": "Specific testable criterion",
              "behavioral_impact": "local|cross-surface|journey",
              "proof_seam": "unit|integration|app-level|process-level|e2e"
            }
          ],
          "sources": [
            {"file": "[source_file]", "lines": "[relevant line range]"}
          ]
        }
      ],
      "scenarios": [
        {
          "title": "Journey title from spec",
          "kind": "journey",
          "proof_seam": "e2e",
          "preconditions": ["from the spec's Pre-conditions section"],
          "steps": [
            {
              "action": "User action or system event from step N",
              "expected": [
                "System response 1 from step N",
                "System response 2 from step N"
              ]
            }
          ],
          "final_observables": [
            "What must be true when the journey completes"
          ],
          "owning_story_titles": ["titles of stories this journey exercises"],
          "sources": [
            {"file": "[source_file]", "lines": "[relevant line range]"}
          ]
        }
      ]
    }

    ### Journey-Specific Rules

    - Preserve the COMPLETE step sequence from the spec — do not skip or summarize steps
    - Each step in the journey becomes one entry in "steps"
    - User actions and system responses from the same spec step go in one steps entry
    - The journey scenario's proof_seam is ALWAYS "e2e"
    - All story ACs that describe behavior within this journey should reference this journey scenario
    - A single journey may produce many stories (one per implementable subsystem touched)

    ### Story Rules (same as standard extraction)

    - Every AC MUST include behavioral_impact and proof_seam
    - Journey ACs that describe assembled behavior get proof_seam "e2e"
    - ACs for internal subsystem details within the journey can use lower seams
    - Sources must cite the specific file and line range
    - Do NOT assign IDs — the aggregator does that

    Output ONLY the JSON object. No other text, no markdown fences, no explanation.
~~~
```

- [ ] **Step 2: Verify the prompt references the correct JSON format from `behavior-evidence-formats.md`**

Read `skills/shared/behavior-evidence-formats.md` and confirm the JSON format in the extraction subagent prompt matches the "Extraction JSON Format (Extended)" section.

- [ ] **Step 3: Commit**

```bash
git add skills/extracting-requirements/extraction-subagent-prompt.md
git commit -m "feat: extend extraction subagent prompt for scenarios and proof obligations"
```

---

## Task 3: Extend story aggregation for proof obligations

**Files:**
- Modify: `skills/extracting-requirements/scripts/aggregate_stories.py`

The story format now includes structured ACs with behavioral_impact and proof_seam. The aggregator must preserve these fields.

- [ ] **Step 1: Update the `format_epic_file` function to emit proof obligations**

In `skills/extracting-requirements/scripts/aggregate_stories.py`, replace the AC formatting in `format_epic_file` (around lines 106-108):

Old:
```python
        lines.append("**Acceptance criteria:**")
        for ac in story.get("acceptance_criteria", []):
            lines.append(f"- {ac}")
```

New:
```python
        lines.append("**Acceptance criteria:**")
        for ac in story.get("acceptance_criteria", []):
            if isinstance(ac, dict):
                ac_text = ac.get("text", "")
                ac_id = ac.get("id", "")
                impact = ac.get("behavioral_impact", "")
                seam = ac.get("proof_seam", "")
                line = f"- {ac_id}: {ac_text}"
                if impact:
                    line += f" · impact:`{impact}`"
                if seam:
                    line += f" · seam:`{seam}`"
                lines.append(line)
            else:
                # Legacy plain-string AC format
                lines.append(f"- {ac}")
```

- [ ] **Step 2: Run the existing tests against the modified script**

```bash
cd skills/extracting-requirements/scripts
python3 -c "
from aggregate_stories import format_epic_file
# Test with new AC format
stories = [{
    '_id': 'STORY-0001',
    '_epic_id': 'EPIC-001',
    '_epic_theme': 'Test',
    'title': 'Test story',
    'as_a': 'user',
    'i_want': 'to test',
    'so_that': 'it works',
    'acceptance_criteria': [
        {'id': 'AC-1', 'text': 'Thing happens', 'behavioral_impact': 'local', 'proof_seam': 'integration'},
        {'id': 'AC-2', 'text': 'Internal detail', 'behavioral_impact': 'none', 'proof_seam': 'unit'}
    ],
    'sources': [{'file': 'test.md', 'lines': '1-10'}]
}]
output = format_epic_file('EPIC-001', 'Test', stories)
assert 'impact:\`local\`' in output, 'Missing impact field'
assert 'seam:\`integration\`' in output, 'Missing seam field'
print('OK: proof obligations preserved in output')
"
```

Expected: `OK: proof obligations preserved in output`

- [ ] **Step 3: Commit**

```bash
git add skills/extracting-requirements/scripts/aggregate_stories.py
git commit -m "feat: extend story aggregation to preserve proof obligations per AC"
```

---

## Task 4: Add scenario aggregation script

**Files:**
- Create: `skills/extracting-requirements/scripts/aggregate_scenarios.py`

Combines scenario JSONs from extraction subagents into `behavior-scenarios.md` with stable IDs.

- [ ] **Step 1: Write the scenario aggregation script**

Write `skills/extracting-requirements/scripts/aggregate_scenarios.py`:

```python
#!/usr/bin/env python3
"""Aggregate extracted scenario JSONs into behavior-scenarios.md.

Usage: aggregate_scenarios.py -o <output-file> --stories-dir <requirements-dir> <json-file>...

Takes one or more JSON files (each containing {"scenarios": [...]}),
deduplicates by title, assigns stable IDs (SCENARIO-NNNN for surface,
JOURNEY-NNNN for journey), resolves owning_story_titles to STORY-IDs
using the requirements directory, and writes behavior-scenarios.md.
"""
import argparse
import json
import re
import sys
from collections import OrderedDict
from pathlib import Path


def load_scenarios(paths: list[Path]) -> list[dict]:
    """Load and combine scenarios from multiple JSON files."""
    all_scenarios: list[dict] = []
    for p in paths:
        data = json.loads(p.read_text())
        if isinstance(data, dict) and "scenarios" in data:
            all_scenarios.extend(data["scenarios"])
        elif isinstance(data, list):
            all_scenarios.extend(data)
    return all_scenarios


def load_story_title_to_id(stories_dir: Path) -> dict[str, str]:
    """Build a title → STORY-ID map from per-epic requirement files."""
    title_map: dict[str, str] = {}
    for epic_file in sorted(stories_dir.glob("EPIC-*.md")):
        text = epic_file.read_text()
        current_id = None
        for line in text.splitlines():
            id_match = re.match(r"^## (STORY-\d+)", line)
            if id_match:
                current_id = id_match.group(1)
            title_match = re.match(r"\*\*Title:\*\* (.+)", line)
            if title_match and current_id:
                title_map[title_match.group(1).strip()] = current_id
                current_id = None
    return title_map


def dedup_scenarios(scenarios: list[dict]) -> list[dict]:
    """Deduplicate scenarios by exact title match."""
    seen: dict[str, dict] = OrderedDict()
    for scenario in scenarios:
        title = scenario.get("title", "").strip()
        if title not in seen:
            seen[title] = dict(scenario)
        else:
            # Merge owning_story_titles and sources
            existing = seen[title]
            for t in scenario.get("owning_story_titles", []):
                if t not in existing.get("owning_story_titles", []):
                    existing.setdefault("owning_story_titles", []).append(t)
            for s in scenario.get("sources", []):
                if s not in existing.get("sources", []):
                    existing.setdefault("sources", []).append(s)
    return list(seen.values())


def assign_ids(scenarios: list[dict]) -> None:
    """Assign stable SCENARIO-NNNN or JOURNEY-NNNN IDs."""
    scenario_counter = 1
    journey_counter = 1
    for s in scenarios:
        if s.get("kind") == "journey":
            s["_id"] = f"JOURNEY-{journey_counter:04d}"
            journey_counter += 1
        else:
            s["_id"] = f"SCENARIO-{scenario_counter:04d}"
            scenario_counter += 1


def resolve_story_refs(scenarios: list[dict], title_map: dict[str, str]) -> None:
    """Replace owning_story_titles with resolved STORY-IDs where possible."""
    for s in scenarios:
        resolved = []
        for title in s.get("owning_story_titles", []):
            story_id = title_map.get(title.strip())
            if story_id:
                resolved.append(story_id)
            else:
                resolved.append(f"UNRESOLVED({title})")
        s["_owning_stories"] = resolved


def format_scenario(s: dict) -> str:
    """Format one scenario as markdown."""
    lines: list[str] = []
    sid = s["_id"]
    title = s.get("title", "Untitled")
    lines.append(f"## {sid} — {title}")
    lines.append("")

    kind = s.get("kind", "surface")
    seam = s.get("proof_seam", "unknown")
    stories = ", ".join(s.get("_owning_stories", []))

    if kind == "journey":
        lines.append(f"**Kind:** journey")
        lines.append(f"**Proof seam:** e2e")
    else:
        lines.append(f"**Kind:** {kind}")
        lines.append(f"**Proof seam:** {seam}")

    lines.append(f"**Owning stories:** {stories}")
    lines.append("")

    lines.append("**Preconditions:**")
    for p in s.get("preconditions", []):
        lines.append(f"- {p}")
    lines.append("")

    if kind == "journey":
        lines.append("**Steps:**")
        for i, step in enumerate(s.get("steps", []), 1):
            action = step.get("action", "")
            lines.append(f"{i}. {action}")
            for exp in step.get("expected", []):
                lines.append(f"   → {exp}")
        lines.append("")
        lines.append("**Final observables:**")
        for obs in s.get("final_observables", []):
            lines.append(f"- {obs}")
    else:
        lines.append("**Action:**")
        for step in s.get("steps", []):
            lines.append(f"- {step.get('action', '')}")
        lines.append("")
        lines.append("**Expected observables:**")
        for step in s.get("steps", []):
            for exp in step.get("expected", []):
                lines.append(f"- {exp}")
        for obs in s.get("final_observables", []):
            lines.append(f"- {obs}")
    lines.append("")

    lines.append("**Automation status:** pending")
    lines.append("**Execution command:** TBD")
    lines.append("")

    lines.append("**Sources:**")
    for src in s.get("sources", []):
        if isinstance(src, dict):
            f = src.get("file", "")
            l = src.get("lines", "")
            lines.append(f"- `{f}:{l}`" if l else f"- `{f}`")
        elif isinstance(src, str):
            lines.append(f"- `{src}`")
    lines.append("")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Aggregate scenarios into behavior-scenarios.md")
    parser.add_argument("-o", "--output", required=True, help="Output file path")
    parser.add_argument("--stories-dir", required=True,
                        help="Requirements directory for resolving story title → ID")
    parser.add_argument("json_files", nargs="+", help="Extracted scenario JSON files")
    args = parser.parse_args()

    paths = [Path(p) for p in args.json_files]
    for p in paths:
        if not p.exists():
            print(f"error: file not found: {p}", file=sys.stderr)
            return 2

    stories_dir = Path(args.stories_dir)
    if not stories_dir.is_dir():
        print(f"error: stories directory not found: {stories_dir}", file=sys.stderr)
        return 2

    scenarios = load_scenarios(paths)
    if not scenarios:
        print("warning: no scenarios found in input files", file=sys.stderr)
        Path(args.output).write_text("# Behavior Scenarios\n\nNo scenarios extracted.\n")
        return 0

    deduped = dedup_scenarios(scenarios)
    assign_ids(deduped)

    title_map = load_story_title_to_id(stories_dir)
    resolve_story_refs(deduped, title_map)

    # Separate journeys and surface scenarios
    journeys = [s for s in deduped if s.get("kind") == "journey"]
    surfaces = [s for s in deduped if s.get("kind") != "journey"]

    lines: list[str] = ["# Behavior Scenarios", ""]

    if journeys:
        lines.append("## Journey Scenarios")
        lines.append("")
        for s in journeys:
            lines.append(format_scenario(s))

    if surfaces:
        lines.append("## Surface Scenarios")
        lines.append("")
        for s in surfaces:
            lines.append(format_scenario(s))

    Path(args.output).write_text("\n".join(lines))

    print(f"OK: {len(journeys)} journey scenarios, {len(surfaces)} surface scenarios")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Verify the script runs without errors on empty input**

```bash
cd skills/extracting-requirements/scripts
echo '{"scenarios": []}' > /tmp/test-empty-scenarios.json
mkdir -p /tmp/test-stories-dir
python3 aggregate_scenarios.py -o /tmp/test-scenarios.md --stories-dir /tmp/test-stories-dir /tmp/test-empty-scenarios.json
cat /tmp/test-scenarios.md
```

Expected: `warning: no scenarios found in input files` and file contains `# Behavior Scenarios`

- [ ] **Step 3: Verify the script handles a complete scenario**

```bash
cd skills/extracting-requirements/scripts
cat > /tmp/test-scenario.json << 'TESTEOF'
{"scenarios": [{"title": "Open settings from menu", "kind": "surface", "proof_seam": "app-level", "preconditions": ["app launched"], "steps": [{"action": "choose Settings from menu", "expected": ["settings window appears"]}], "final_observables": ["window titled Settings visible"], "owning_story_titles": ["Open settings window"], "sources": [{"file": "test.md", "lines": "1-10"}]}]}
TESTEOF
python3 aggregate_scenarios.py -o /tmp/test-scenarios.md --stories-dir /tmp/test-stories-dir /tmp/test-scenario.json
cat /tmp/test-scenarios.md
```

Expected: output contains `## SCENARIO-0001 — Open settings from menu` with all fields populated

- [ ] **Step 4: Commit**

```bash
git add skills/extracting-requirements/scripts/aggregate_scenarios.py
git commit -m "feat: add scenario aggregation script"
```

---

## Task 5: Rewrite extracting-requirements skill for behavior evidence

**Files:**
- Modify: `skills/extracting-requirements/SKILL.md`

The extraction pipeline gains scenario extraction steps, an extended coverage ledger with scenario coverage, and a hard gate on scenario gaps.

- [ ] **Step 1: Rewrite the extracting-requirements skill**

Replace the full content of `skills/extracting-requirements/SKILL.md` with:

```markdown
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

After both aggregations complete, update the per-epic story files with scenario references. For each story whose ACs reference scenarios:

1. Read the scenario file to find SCENARIO/JOURNEY IDs
2. Match scenarios to stories via `owning_stories`
3. Append `scenario:SCENARIO-NNNN` or `scenario:JOURNEY-NNNN` to the relevant AC lines in the story files

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
| Back-link | Manual or scripted | scenarios + stories | Updated AC lines with scenario refs |
| Coverage ledger | Map chunks → story IDs + scenario IDs | chunk list, stories, scenarios | Gap/covered/story-only per chunk |
| Init corpus | Write corpus index | scenario list | `behavior-corpus.md` |
| Validate | `scripts/validate_requirements_index.py` + `scripts/validate_scenarios.py` | .md files | OK or errors |

## Deferred to later plans

Hierarchical reduce (specs > 1M tokens), huge-spec decomposition, incremental re-extraction, automated back-linking script.
```

- [ ] **Step 2: Verify cross-references**

Read the new SKILL.md and check that every referenced file exists or will be created by another task:
- `skills/shared/behavior-evidence-formats.md` — created in Task 1
- `extraction-subagent-prompt.md` — modified in Task 2
- `scripts/chunk_spec.py` — exists
- `scripts/aggregate_stories.py` — modified in Task 3
- `scripts/aggregate_scenarios.py` — created in Task 4
- `scripts/validate_requirements_index.py` — exists
- `scripts/validate_scenarios.py` — created in Task 12
- `skills/shared/parallel-adversarial-review.md` — exists

- [ ] **Step 3: Commit**

```bash
git add skills/extracting-requirements/SKILL.md
git commit -m "feat: rewrite extracting-requirements for behavior evidence pipeline"
```

---

## Task 6: Extend scoping for story splitting and skeleton scenarios

**Files:**
- Modify: `skills/scoping-the-simplest-core/SKILL.md`

Scoping gains: (1) story splitting when moving stories with heterogeneous-dependency ACs, (2) walking skeleton must produce first runnable journey scenario, (3) scope reviewer checks scenario coverage.

- [ ] **Step 1: Rewrite the scoping skill**

Replace the full content of `skills/scoping-the-simplest-core/SKILL.md` with:

```markdown
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
```

- [ ] **Step 2: Commit**

```bash
git add skills/scoping-the-simplest-core/SKILL.md
git commit -m "feat: extend scoping for story splitting and skeleton journey scenarios"
```

---

## Task 7: Update scope reviewer for scenario coverage

**Files:**
- Modify: `skills/running-an-iteration/scope-reviewer-prompt.md`

The scope reviewer gains two new checks: scenario coverage and story splitting.

- [ ] **Step 1: Rewrite the scope reviewer prompt**

Replace the full content of `skills/running-an-iteration/scope-reviewer-prompt.md` with:

```markdown
# Scope Reviewer Prompt Template

Use this template inside the PAR wrapper when dispatching scope review subagents before an iteration starts.

~~~
[REVIEWER INSTRUCTIONS — insert inside PAR wrapper from skills/shared/par-reviewer-wrapper.md]

You are reviewing the scope of an upcoming iteration BEFORE any code is written.

## Iteration Being Reviewed

[Paste the iteration entry from roadmap.md — stories committed, rationale, impacted scenarios]

## Stories in Scope

[For each committed story, paste the full story card from the requirements directory, including proof obligations per AC]

## Scenarios Impacted

[List all scenarios (from behavior-scenarios.md) whose owning stories appear in this iteration's scope]

## Next 3 Pending Iterations

[Paste the next 3 iteration entries from roadmap.md for look-ahead]

## Your Five Checks

### 1. Citation Integrity

For every story committed to this iteration:
- Does it cite a valid STORY-NNNN that exists in the requirements directory?
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
- Does this iteration introduce hard coupling, premature abstraction, or structural commitments that would need to be undone?
- Could the same functionality be achieved with fewer commitments?

If you can identify a specific downstream iteration that would be blocked by a choice made in this iteration, that's a CRITICAL finding.

### 4. Scenario Coverage

- Does this iteration leave any externally observable behavior without planned scenario coverage?
- For each story with ACs that have behavioral_impact other than "none": is there a scenario that covers it?
- For ITER-0000 specifically: does the walking skeleton close at least one journey scenario?

If the iteration would deliver observable behavior but add zero scenarios, that is a SERIOUS finding.

### 5. Story Splitting

- Are there stories in this iteration whose ACs have different dependency profiles?
- Does any AC depend on a subsystem that won't exist until a later iteration while other ACs in the same story can be satisfied now?
- If so, recommend splitting: which ACs stay, which move, and to which iteration?

If a story with heterogeneous-dependency ACs is scoped whole into one iteration, that is a SERIOUS finding.

## Report Format

For each check:
- **Citation Integrity:** [PASS | issues found]
- **Scope Creep:** [PASS | recommendations to defer/split]
- **Boxing-In:** [PASS | risks identified with specific downstream iterations affected]
- **Scenario Coverage:** [PASS | observable behavior without planned scenarios]
- **Story Splitting:** [PASS | stories that should be split, with specific AC breakdown]

Overall: [APPROVE | REVISE — with specific changes needed]
~~~
```

- [ ] **Step 2: Commit**

```bash
git add skills/running-an-iteration/scope-reviewer-prompt.md
git commit -m "feat: extend scope reviewer for scenario coverage and story splitting checks"
```

---

## Task 8: Extend running-an-iteration for evidence tasks and sentinel corpus

**Files:**
- Modify: `skills/running-an-iteration/SKILL.md`

Iteration planning now decomposes into code tasks AND evidence tasks. Pre- and post-iteration sentinel corpus runs are added.

- [ ] **Step 1: Rewrite the running-an-iteration skill**

Replace the full content of `skills/running-an-iteration/SKILL.md` with:

```markdown
---
name: running-an-iteration
description: Use when executing the next pending iteration from an iterative-development roadmap — picks the iteration, decomposes into code and evidence tasks, runs sentinel corpus baseline, dispatches implementing-tasks, runs impacted + sentinel scenarios, and updates artifacts.
---

# Running an Iteration

## Overview

Drives one iteration: picks the next pending, runs sentinel corpus baseline, runs pre-iteration scope review via PAR, decomposes into code and evidence tasks, dispatches `implementing-tasks`, runs impacted + sentinel scenarios at wrap-up, and updates the roadmap and iteration log.

## When to Use

Invoked by `iterative-development` inside the main loop. Each invocation runs exactly one iteration. After return, the orchestrator invokes `auditing-progress`.

## Script Location

All scripts referenced below live in this skill's `scripts/` directory, next to this SKILL.md file.

## Iteration Process

### 1. Pick next iteration

Read `docs/superpowers/iterations/roadmap.md`, find the first iteration with status `pending`.

### 2. Load scope context

Read the per-epic files in `docs/superpowers/iterations/requirements/` to load the full story cards for each committed story ID. Only read the epic files that contain stories for this iteration — not all of them. Also:
- Load the next 3 pending iterations from the roadmap for look-ahead
- Read `docs/superpowers/iterations/behavior-scenarios.md` to identify impacted scenarios
- Read `docs/superpowers/iterations/behavior-corpus.md` to identify sentinel scenarios

### 3. Run sentinel corpus baseline

Before any code changes, run every scenario in the behavior corpus with run cadence `sentinel`:

- If all sentinels pass: record baseline as clean, proceed
- If any sentinel fails: the failure predates this iteration. Record it, create a gap story for it, but proceed with the iteration (the gap will be addressed in a follow-up)

This establishes whether regressions exist before the current iteration starts.

### 4. Pre-iteration consistency audit

Before planning any work, verify that artifact state is consistent:

1. **Citation check:** `python3 "scripts/check_citations.py" docs/superpowers/iterations/roadmap.md docs/superpowers/iterations/requirements/` — if citations fail, stop and fix the roadmap.
2. **Status reconciliation:** For each story in this iteration's scope, verify:
   - Stories listed in the roadmap iteration are not already marked `done:ITER-XXXX` in the requirements index (unless code/tests actually exist for them)
   - Stories marked `done` in the requirements index actually have corresponding code and tests
   - No story appears in multiple pending iterations
3. **Epic counter validation:** Spot-check that epic progress counters match the actual count of `done` stories.

If any inconsistencies are found, reconcile before proceeding. Do not trust any single artifact blindly — cross-check.

### 5. Pre-iteration scope review (PAR)

Following `skills/shared/parallel-adversarial-review.md`:

1. Build the scope reviewer prompt using `scope-reviewer-prompt.md`
2. Wrap in PAR competitive framing from `skills/shared/par-reviewer-wrapper.md`
3. Dispatch TWO scope reviewers in parallel (Agent tool, two calls in one message)
4. Aggregate findings: same issue from both = high confidence, unique = still actionable, severity disagreement = take worst
5. If REVISE recommended: adjust iteration scope and re-review. Loop until APPROVE.

### 6. Decompose into code tasks AND evidence tasks

Break the iteration scope into TDD-sized tasks. Each task = failing test → implementation → passing test → commit.

**Evidence tasks:** In addition to code tasks, identify:
- Which existing scenarios are impacted by this iteration's changes
- Which new scenarios must be added (from the story proof obligations)
- Which scenario harnesses need to be extended
- Which behavior corpus entries need updated execution commands

Evidence tasks are first-class — they produce scenario updates, test harness extensions, and corpus index entries. They are NOT afterthoughts. Interleave evidence tasks with code tasks: after implementing a feature, the next task should be extending or adding the scenario that proves it.

**Cross-iteration dependencies:** Some stories reference subsystems that don't exist yet. For these, implement a protocol/abstraction that satisfies the story's ACs without coupling to the future implementation. Document the dependency with a TODO comment citing the future iteration. Do NOT defer the story silently or force premature integration.

### 7. Dispatch implementing-tasks

Pass the task list (code + evidence tasks) and iteration context to `implementing-tasks`. Wait for completion.

### 8. Post-iteration scenario runs

After all tasks complete, run:

1. **Impacted scenarios:** every scenario in the behavior corpus whose owning stories were touched by this iteration
2. **Sentinel scenarios:** every scenario with run cadence `sentinel`

If any impacted or sentinel scenario fails that passed at baseline (step 3), this iteration introduced a regression. Create a fix task and re-dispatch to `implementing-tasks`.

### 9. Wrap up

- Verify all iteration stories' ACs pass (sanity check before audit)
- Verify all proof obligations for observable ACs have corresponding scenario evidence
- Mark stories `done:ITER-NNNN` in the relevant epic files under `requirements/`
- Update scenario automation status and execution commands in `behavior-scenarios.md`
- Update the behavior corpus index in `behavior-corpus.md`
- Update iteration status in `roadmap.md` to `done`
- Append entry to `docs/superpowers/iterations/iteration-log.md` — include:
  - Stories delivered
  - Scenarios added or updated
  - Sentinel corpus results
- Validate: `python3 "scripts/validate_iteration_log.py" docs/superpowers/iterations/iteration-log.md`
- Return control to orchestrator (do NOT invoke `auditing-progress` — that's the orchestrator's job)

## Quick Reference

| Step | Tool/Skill | Purpose |
|---|---|---|
| Sentinel baseline | Run sentinel scenarios | Establish pre-iteration regression state |
| Citation check | `scripts/check_citations.py` | Mechanical: cited stories exist |
| Scope review | PAR + `scope-reviewer-prompt.md` | Semantic: scope, scenarios, splitting, boxing-in |
| Task execution | `implementing-tasks` | TDD code + evidence implementation |
| Post-iteration runs | Run impacted + sentinel scenarios | Catch regressions |
| Wrap up | `scripts/validate_iteration_log.py` | Artifact validation |

## References

- `skills/shared/parallel-adversarial-review.md` — PAR methodology
- `skills/shared/behavior-evidence-formats.md` — scenario and proof obligation formats
- `scope-reviewer-prompt.md` — scope reviewer prompt template
- `scripts/check_citations.py` — mechanical citation check
```

- [ ] **Step 2: Commit**

```bash
git add skills/running-an-iteration/SKILL.md
git commit -m "feat: extend iteration planning for evidence tasks and sentinel corpus runs"
```

---

## Task 9: Extend implementer prompt for proof obligations

**Files:**
- Modify: `skills/implementing-tasks/implementer-subagent-prompt.md`

The implementer now performs an AC → proof seam pre-flight mapping before coding and must update the behavior corpus when observable behavior changes.

- [ ] **Step 1: Rewrite the implementer subagent prompt**

Replace the full content of `skills/implementing-tasks/implementer-subagent-prompt.md` with:

```markdown
# Implementer Subagent Prompt Template

Use this template when dispatching an implementer subagent for a single task.

~~~
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

    ## Proof Obligations

    [For each AC in the task's stories that has behavioral_impact other than
    "none", list: AC-N, proof seam, scenario to update or create]

    ## Before You Begin — Pre-Flight Mapping

    Before writing any code, state:

    1. Which ACs affect externally observable behavior
    2. What proof seam each observable AC requires
    3. Which existing scenario you will extend, OR what new scenario you will add
    4. What test harness or command will prove the behavior

    If the task changes observable behavior and you cannot identify a scenario
    to update or create, STOP and report NEEDS_CONTEXT. Do not proceed without
    a proof obligation plan.

    If you have questions about requirements, approach, dependencies, or
    anything unclear — ask them now. Don't guess or make assumptions.

    ## Your Job

    1. State your pre-flight mapping (above)
    2. Follow TDD red-green-refactor (superpowers:test-driven-development):
       - Write the failing test first
       - Run it to verify it fails
       - Write the minimal implementation to make it pass
       - Run to verify it passes
       - Refactor if needed
    3. If observable behavior changed: update or add the behavior scenario
       - Update scenario card in behavior-scenarios.md (or note the update for the caller)
       - Update or add the test harness that proves the scenario
       - Update the behavior corpus index with the execution command
    4. Commit your work when tests pass
    5. Self-review before reporting

    ## Self-Review Checklist

    Before reporting, ask yourself:
    - Did I implement exactly what was specified? (nothing more, nothing less)
    - Are names clear and domain-appropriate?
    - Did I follow TDD discipline? (test before implementation)
    - Do tests verify real behavior, not mock behavior?
    - Did I follow existing codebase patterns?
    - **Did I update the behavior corpus for every observable AC I changed?**
    - **Is the evidence at the correct proof seam? (not weaker than declared)**

    Fix any issues found during self-review before reporting.

    ## Report Format

    - **Status:** DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
    - **Pre-flight mapping:** [which ACs, which seams, which scenarios]
    - What you implemented
    - What you tested and results
    - **Scenarios added or updated:** [list]
    - **Evidence commands:** [how to run the behavior proof]
    - Files changed
    - Self-review findings (if any)
    - Concerns (if DONE_WITH_CONCERNS)

    DONE_WITH_CONCERNS = completed but have doubts about correctness.
    BLOCKED = cannot complete. NEEDS_CONTEXT = missing information.
    Never silently produce work you're unsure about.
~~~
```

- [ ] **Step 2: Commit**

```bash
git add skills/implementing-tasks/implementer-subagent-prompt.md
git commit -m "feat: extend implementer prompt with proof obligation pre-flight and corpus updates"
```

---

## Task 10: Extend spec-compliance reviewer for evidence quality

**Files:**
- Modify: `skills/implementing-tasks/spec-compliance-reviewer-prompt.md`

The spec-compliance reviewer now also checks whether behavior evidence exists at the correct seam.

- [ ] **Step 1: Rewrite the spec-compliance reviewer prompt**

Replace the full content of `skills/implementing-tasks/spec-compliance-reviewer-prompt.md` with:

```markdown
# Spec-Compliance Reviewer Prompt Template

Use this template INSIDE the PAR wrapper when dispatching spec-compliance reviewers. This is Stage 1 of the two-stage review — it runs BEFORE code-quality review.

~~~
[REVIEWER INSTRUCTIONS — insert inside PAR wrapper from skills/shared/par-reviewer-wrapper.md]

You are reviewing whether an implementation matches its specification AND
whether behavior evidence exists at the correct seam.

## What Was Requested

[FULL task description that was given to the implementer — paste it here,
including the proof obligations for each observable AC]

## What the Implementer Claims They Built

[From the implementer's status report — what they say they did, including
their pre-flight mapping and scenarios added/updated]

## CRITICAL: Do Not Trust the Report

The implementer may be incomplete, inaccurate, or optimistic. Verify
everything independently by reading the actual code.

DO NOT:
- Take their word for what they implemented
- Trust claims about completeness
- Accept their interpretation of requirements
- Accept claims about scenario coverage without checking

DO:
- Read the actual code they wrote
- Compare implementation to requirements line by line
- Check for missing pieces
- Look for extra features not requested
- Verify behavior evidence exists and is at the right seam

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

**Evidence quality:**
- For each AC with behavioral_impact other than "none":
  - Does a scenario exist that covers this AC?
  - Is the evidence at the declared proof seam (not weaker)?
  - Does the test or harness actually prove the observable behavior?
- REJECT: unit-only evidence for app-level or e2e behavior
- REJECT: inspection-only evidence without strong justification
- REJECT: one-time manual verification that did not update the behavior corpus
- If the task changed observable behavior but added no scenario or harness: CRITICAL finding

## Report Format

For each finding, cite the specific file:line reference.

**Spec Compliance:** ✅ Compliant | ❌ Issues found: [list]
**Evidence Quality:** ✅ Adequate | ❌ Weak evidence: [list with seam analysis]

Overall: ✅ Spec compliant with adequate evidence | ❌ Issues found: [list]
~~~
```

- [ ] **Step 2: Commit**

```bash
git add skills/implementing-tasks/spec-compliance-reviewer-prompt.md
git commit -m "feat: extend spec-compliance reviewer to check evidence quality at correct seam"
```

---

## Task 11: Extend code-quality reviewer for corpus contribution

**Files:**
- Modify: `skills/implementing-tasks/code-quality-reviewer-prompt.md`

The code-quality reviewer now inspects the quality of the corpus contribution itself.

- [ ] **Step 1: Rewrite the code-quality reviewer prompt**

Replace the full content of `skills/implementing-tasks/code-quality-reviewer-prompt.md` with:

```markdown
# Code-Quality Reviewer Prompt Template

Use this template INSIDE the PAR wrapper when dispatching code-quality reviewers. This is Stage 2 of the two-stage review — it runs AFTER spec-compliance review passes.

~~~
[REVIEWER INSTRUCTIONS — insert inside PAR wrapper from skills/shared/par-reviewer-wrapper.md]

You are reviewing code quality, architectural soundness, and behavior
corpus contribution quality.

## What Was Implemented

[From the implementer's report — summary of what was built, including
scenarios added/updated and evidence commands]

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

### Corpus Contribution Quality

If the implementer added or updated behavior scenarios:
- Is the scenario clearly written and reusable?
- Is the test harness narrowly scoped and maintainable?
- Does the scenario prove observable behavior, not implementation detail?
- Could the scenario survive a significant refactor without breaking?
- Does the execution command actually work?
- Is the proof seam appropriate (not too weak, not unnecessarily heavy)?

If the implementation boxes future scenarios into a brittle seam (e.g.,
testing via private internals when a public interface would be stable),
that's a SERIOUS finding.

### Report Format

**Strengths:** [brief list]

**Issues:**
- Critical: [blocks correctness or downstream work — file:line refs]
- Serious: [significant quality problem — file:line refs]
- Minor: [style, naming — file:line refs]

**Boxing-In Assessment:** [CLEAR | RISK — with specific downstream iterations affected]
**Corpus Quality:** [GOOD | WEAK — with specific scenario/harness issues]

**Overall:** ✅ Approved | ❌ Changes needed
~~~
```

- [ ] **Step 2: Commit**

```bash
git add skills/implementing-tasks/code-quality-reviewer-prompt.md
git commit -m "feat: extend code-quality reviewer for corpus contribution inspection"
```

---

## Task 12: Extend implementing-tasks skill for evidence framing

**Files:**
- Modify: `skills/implementing-tasks/SKILL.md`

The skill now frames tasks as "implement + attach evidence" and requires corpus updates for observable behavior changes.

- [ ] **Step 1: Update implementing-tasks SKILL.md**

In `skills/implementing-tasks/SKILL.md`, add the following after the existing "Per-Task Cycle" heading (before step 1):

Replace the existing content after `## Per-Task Cycle` and before `## Model Selection` with:

```markdown
## Per-Task Cycle

For each task in the provided list:

### 1. Dispatch implementer

Using the template in `implementer-subagent-prompt.md`, dispatch a single implementer subagent with:
- The full task description and context
- The proof obligations for each observable AC in the task's stories
- The list of existing scenarios that may be impacted

The implementer MUST complete a pre-flight mapping (AC → proof seam → scenario) before writing code. If the implementer skips the pre-flight, re-dispatch with explicit instructions to complete it first.

### 2. Handle implementer status

- **DONE:** proceed to spec-compliance review (step 3). Verify the implementer's report includes pre-flight mapping and scenario updates.
- **DONE_WITH_CONCERNS:** read the concerns. If about correctness/scope, address before review. If observations, note and proceed.
- **NEEDS_CONTEXT:** provide the missing context and re-dispatch
- **BLOCKED:** assess: context problem → re-dispatch with context; too hard → re-dispatch with more capable model; task too large → break into smaller pieces; plan wrong → escalate to caller

### 3. PAR spec-compliance review (Stage 1)

Following `skills/shared/parallel-adversarial-review.md`:

1. Build spec-compliance prompt using `spec-compliance-reviewer-prompt.md`
   - Include the proof obligations and the implementer's evidence claims
2. Wrap in PAR competitive framing from `skills/shared/par-reviewer-wrapper.md`
3. Dispatch TWO spec-compliance reviewers in parallel
4. Aggregate findings (PAR rules: union of findings, severity = take worst)
5. If ❌ issues found:
   - Send aggregated issues back to the implementer subagent (same subagent, via SendMessage)
   - Implementer fixes
   - Re-dispatch fresh PAR spec-compliance pair
   - Repeat until ✅ spec compliant with adequate evidence
6. Only proceed to Stage 2 after Stage 1 is ✅

### 4. PAR code-quality review (Stage 2)

Following `skills/shared/parallel-adversarial-review.md`:

1. Build code-quality prompt using `code-quality-reviewer-prompt.md`
   - Include the next 3 pending roadmap iterations for the boxing-in check
   - Include the implementer's corpus contribution for quality review
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

After all tasks complete, return a per-task result list to the caller, including:
- Per-task status
- Scenarios added or updated per task
- Evidence commands per task
```

- [ ] **Step 2: Commit**

```bash
git add skills/implementing-tasks/SKILL.md
git commit -m "feat: extend implementing-tasks with evidence framing and corpus update requirements"
```

---

## Task 13: Rewrite auditor prompt for three-tier evidence audit

**Files:**
- Modify: `skills/auditing-progress/auditor-subagent-prompt.md`

The auditor now verifies behavior evidence quality in three tiers, not just code existence.

- [ ] **Step 1: Rewrite the auditor subagent prompt**

Replace the full content of `skills/auditing-progress/auditor-subagent-prompt.md` with:

```markdown
# Auditor Subagent Prompt Template

Use this template when dispatching auditor subagents inside the PAR wrapper. Fill in the bracketed values.

~~~
[REVIEWER INSTRUCTIONS — insert inside PAR wrapper from skills/shared/par-reviewer-wrapper.md]

You are auditing a just-completed iteration's work against its story
acceptance criteria AND verifying that behavior evidence exists at the
correct seam.

## Tier 1: Deep Evidence Audit (current iteration)

### Stories to Audit

[For each story marked done:ITER-<current>, paste the story card including
all acceptance criteria with proof obligations and scenario references]

### Scenarios Added or Updated

[List all scenarios from behavior-scenarios.md that were added or changed
in this iteration]

### Your Job (Tier 1)

For each story:
1. Read the acceptance criteria and their proof obligations
2. Find the tests and code that claim to implement each AC
3. Run the tests
4. Verify each AC is actually met — not just that tests pass, but that
   the tests actually TEST what the AC requires
5. For each AC with behavioral_impact other than "none":
   - Verify a scenario exists with the declared proof seam
   - Verify the scenario's test/harness proves the observable behavior
   - Verify the evidence is at the correct seam (not weaker than declared)
   - REJECT: unit-only evidence for app-level behavior
   - REJECT: code inspection without test evidence (unless explicitly justified)
6. Flag any AC that is NOT met with:
   - The story ID and AC number
   - What the AC requires
   - What the code/tests actually do
   - Whether the evidence seam is adequate
   - Why there is a gap

## Tier 2: Impacted Behavior Audit

### Existing Scenarios Touched by This Iteration

[List all scenarios from behavior-scenarios.md whose owning stories had
code changes in this iteration, even if the stories were completed in
earlier iterations]

### Your Job (Tier 2)

For each impacted scenario:
1. Verify the scenario's test/harness still passes
2. Check whether the iteration's code changes affect the scenario's
   expected observables
3. If the scenario needs updating (new behavior, changed behavior),
   verify it was updated
4. Flag scenarios that are now stale or broken

## Tier 3: Sentinel Corpus Audit

### Sentinel Scenarios

[List all scenarios from behavior-corpus.md with run cadence "sentinel"]

### Your Job (Tier 3)

For each sentinel scenario:
1. Run the scenario's execution command (or verify the caller ran it)
2. Compare results against the pre-iteration baseline
3. If a sentinel that passed at baseline now fails: this iteration
   introduced a regression — CRITICAL finding
4. If a sentinel that failed at baseline still fails: note it but do
   not attribute it to this iteration

## Additional Checks

Scan the iteration's git diff for:
- Features, flags, or commands that don't map to any story (unrequested work)
- Commented-out code or debug artifacts left behind
- Observable behavior changes that did not update any scenario

## Report Format

### Tier 1: Deep Evidence
For each story:
- STORY-NNNN: [PASS | FAIL]
  - AC-1: [PASS | FAIL — explanation if fail]
  - Evidence: [ADEQUATE | WEAK — seam analysis if weak]

### Tier 2: Impacted Behavior
For each impacted scenario:
- SCENARIO-NNNN / JOURNEY-NNNN: [PASS | STALE | BROKEN]
  - [explanation if not PASS]

### Tier 3: Sentinel Corpus
For each sentinel:
- JOURNEY-NNNN: [PASS | REGRESSION | PRE-EXISTING FAILURE]

Unrequested features found: [list or "none"]
Observable behavior without corpus update: [list or "none"]

Overall: [CLEAN | GAPS FOUND]
~~~
```

- [ ] **Step 2: Commit**

```bash
git add skills/auditing-progress/auditor-subagent-prompt.md
git commit -m "feat: rewrite auditor prompt for three-tier behavior evidence audit"
```

---

## Task 14: Rewrite auditing-progress skill for three-tier audit

**Files:**
- Modify: `skills/auditing-progress/SKILL.md`

The audit now operates in three tiers: deep evidence (current iteration), impacted behavior (touched surfaces), sentinel corpus (high-value regression guard).

- [ ] **Step 1: Rewrite the auditing-progress skill**

Replace the full content of `skills/auditing-progress/SKILL.md` with:

```markdown
---
name: auditing-progress
description: Use when an iteration has just finished and you need to verify behavior evidence quality in three tiers — deep evidence for current stories, impacted behavior for touched scenarios, and sentinel corpus for high-value regression detection.
---

# Auditing Progress

## Overview

Runs after every iteration as part of the planning cycle. Verifies behavior evidence quality in three tiers using **parallel adversarial review (PAR)** — two paired auditor subagents evaluate the same work in parallel with competitive framing.

The audit answers: "Does durable, reusable evidence exist at the correct seam for every externally observable behavior this iteration touched?"

## When to Use

Invoked by `iterative-development` after every `running-an-iteration` call, before picking the next iteration.

## Audit Process

### 1. Partition the audit into three tiers

Read the per-epic requirement files in `docs/superpowers/iterations/requirements/`, `docs/superpowers/iterations/behavior-scenarios.md`, and `docs/superpowers/iterations/behavior-corpus.md`:

- **Tier 1 — Deep evidence:** stories marked `done:ITER-<current>` and scenarios added or updated in this iteration. Audit every AC and its proof obligation thoroughly.
- **Tier 2 — Impacted behavior:** all existing scenarios whose owning stories had code changes in this iteration (even if those stories were completed in earlier iterations). Verify the scenarios still pass.
- **Tier 3 — Sentinel corpus:** all scenarios with run cadence `sentinel` in the behavior corpus. Compare against the pre-iteration baseline from `running-an-iteration` step 3.

### 2. Dispatch paired auditor subagents (PAR)

Following the PAR methodology in `skills/shared/parallel-adversarial-review.md`:

1. Build the auditor prompt using `auditor-subagent-prompt.md`. Include ALL THREE tiers:
   - Tier 1: full story cards with proof obligations + new/changed scenario cards
   - Tier 2: impacted scenario cards + their current test results
   - Tier 3: sentinel scenario IDs + baseline results + current results
2. Wrap in competitive framing from `skills/shared/par-reviewer-wrapper.md`
3. Dispatch TWO auditor subagents in parallel
4. Wait for both to return

### 3. Aggregate findings

Following PAR aggregation rules:
- Same finding from both auditors → one finding, high confidence
- Finding from only one auditor → separate finding, still actionable
- Severity disagreement → take the more severe assessment, always fix it

### 4. Process results

- **If gaps found** (any AC fails, evidence is too weak, sentinel regression detected):
  - For AC failures: append gap stories to `requirements/` (status `pending`) or flip existing stories back from `done` to `pending`
  - For weak evidence: create evidence-improvement stories (add scenario, strengthen seam)
  - For sentinel regressions: create regression-fix stories with CRITICAL priority
  - Revise `roadmap.md` to add a follow-up iteration for the gaps
- **If clean** (all tiers pass, evidence is adequate):
  - The iteration is confirmed done
  - Return clean signal to the orchestrator

### 5. Return control

Return the audit result (clean or gaps) to the orchestrator. The orchestrator decides whether to loop or terminate.

## Quick Reference

| Tier | What it checks | Failure means |
|---|---|---|
| Deep evidence | Every AC + proof obligation for current iteration | Story not done, evidence too weak |
| Impacted behavior | Scenarios whose surfaces were touched | Stale or broken scenario |
| Sentinel corpus | High-value journey scenarios | Regression in previously-working behavior |

| Reads | Writes | Dispatches |
|---|---|---|
| `requirements/`, `behavior-scenarios.md`, `behavior-corpus.md`, product code/tests | `requirements/` (gaps), `roadmap.md` (new iteration) if gaps, `behavior-scenarios.md` (stale flags) | **Two** auditor subagents in parallel (PAR) |

## References

- `skills/shared/parallel-adversarial-review.md` — PAR methodology
- `skills/shared/par-reviewer-wrapper.md` — competitive framing wrapper
- `skills/shared/behavior-evidence-formats.md` — scenario and proof obligation formats
- `auditor-subagent-prompt.md` — auditor-specific prompt template
```

- [ ] **Step 2: Commit**

```bash
git add skills/auditing-progress/SKILL.md
git commit -m "feat: rewrite auditing-progress for three-tier behavior evidence audit"
```

---

## Task 15: Update orchestrator for behavior evidence completion gate

**Files:**
- Modify: `skills/iterative-development/SKILL.md`

The orchestrator's completion gate shifts from "stories done" to "behavior evidence passes." New artifacts are tracked. Final audit verifies scenario coverage.

- [ ] **Step 1: Update the orchestrator skill**

In `skills/iterative-development/SKILL.md`, make the following changes:

**Replace the description frontmatter:**

Old:
```
description: Use when implementing a project with a large, comprehensive, or ambiguous spec that would overwhelm the writing-plans → subagent-driven-development flow — extracts requirements, defines a walking skeleton, then loops through audited sprints autonomously.
```

New:
```
description: Use when implementing a project with a large, comprehensive, or ambiguous spec — extracts requirements with proof obligations, defines a walking skeleton with its first journey scenario, then loops through audited sprints that continuously build a behavior evidence corpus. Completion means passing evidence, not just finished stories.
```

**Replace the Overview section:**

Old:
```
Orchestrator for the iterative-development plugin. Drives the full autonomous lifecycle: extract requirements from human spec collateral, define a walking skeleton, loop through audited sprints until an auditor confirms the product matches the backlog. Every evaluative gate uses parallel adversarial review (PAR).
```

New:
```
Orchestrator for the iterative-development plugin. Drives the full autonomous lifecycle: extract requirements with proof obligations and behavior scenarios from human spec collateral, define a walking skeleton that passes its first journey scenario, then loop through audited sprints that continuously build a reusable behavior evidence corpus. Completion means the product has passing behavior evidence at the correct seam for every externally observable requirement — not just that stories are marked done. Every evaluative gate uses parallel adversarial review (PAR).
```

**Replace the Bootstrap section step 2:**

Old:
```
2. Invoke `extracting-requirements` on the human-provided spec path.
   - Chunks the spec, dispatches parallel extraction subagents, aggregates results
   - Produces `docs/superpowers/iterations/requirements/`
```

New:
```
2. Invoke `extracting-requirements` on the human-provided spec path.
   - Chunks the spec, classifies by taxonomy (journeys → E2E, domains → integration, etc.)
   - Dispatches parallel extraction subagents that produce stories with proof obligations AND behavior scenarios
   - Aggregates stories into per-epic files, scenarios into behavior-scenarios.md
   - Builds coverage ledger with both story AND scenario coverage
   - Produces `docs/superpowers/iterations/requirements/`, `docs/superpowers/iterations/behavior-scenarios.md`, `docs/superpowers/iterations/behavior-corpus.md`
```

**Replace the Bootstrap section step 3 to add:**

After `Produces docs/superpowers/iterations/roadmap.md`, add:
```
   - Walking skeleton must close at least one journey scenario (not just compile)
   - Applies story splitting when stories have heterogeneous-dependency ACs
```

**Replace the Main loop section:**

Old:
```
while True:
    check_for_human_interrupt()

    if not roadmap has pending iterations:
        if last audit was clean:
            run final spec-surface audit (see below)
            if spec audit clean:
                break  # done
            # else: spec audit found uncovered surfaces, new iterations added
        # else: audit found gaps, new iterations were added, continue

    run next iteration:
        - running-an-iteration (scope review → decompose → implementing-tasks → wrap up)
    
    audit:
        - auditing-progress (PAR paired auditors, two-tier: deep new + sweep whole)
        - if gaps: append to backlog, revise roadmap, continue
        - if clean: mark last_audit_clean, continue
```

New:
```
while True:
    check_for_human_interrupt()

    if not roadmap has pending iterations:
        if last audit was clean:
            run final behavior-evidence audit (see below)
            if behavior audit clean:
                break  # done
            # else: audit found uncovered surfaces or weak evidence, new iterations added
        # else: audit found gaps, new iterations were added, continue

    run next iteration:
        - running-an-iteration (sentinel baseline → scope review → decompose code + evidence tasks → implementing-tasks → impacted + sentinel scenario runs → wrap up)
    
    audit:
        - auditing-progress (PAR paired auditors, three-tier: deep evidence + impacted behavior + sentinel corpus)
        - if gaps: append to backlog, revise roadmap, continue
        - if clean: mark last_audit_clean, continue
```

**Replace the "Final spec-surface audit" section:**

Old title: `### Final spec-surface audit`

New:
```markdown
### Final behavior-evidence audit

Before declaring the project complete, verify that the product has adequate behavior evidence — not just that all stories are marked done:

1. List every major user-facing surface from the original spec (settings panes, UI flows, CLI commands, journeys, etc.)
2. For each surface, verify that:
   - Corresponding stories exist AND are implemented
   - Corresponding scenarios exist AND have passing evidence at the correct seam
   - Journey scenarios that cross multiple surfaces are passing E2E
3. Check the behavior corpus index for completeness:
   - Every journey spec file has at least one JOURNEY-NNNN scenario
   - Every scenario has a non-TBD execution command
   - All sentinel scenarios pass
4. Flag any surface with:
   - No corresponding story (extraction under-scoped)
   - No corresponding scenario (evidence gap)
   - Evidence at a weaker seam than the requirement demands
   - Manual-residual scenarios that could be automated
5. If gaps found: create new stories/scenarios/iterations, continue the loop

The final question is: "Can the system point to passing behavior evidence for every externally observable requirement the spec describes?" Not: "Are the stories done?"
```

**Replace the Artifact Location table:**

Old:
```
| File | Purpose |
|---|---|
| `requirements/` | Backlog: story cards + epics with stable IDs |
| `roadmap.md` | Sprint plan: ordered iterations with status |
| `iteration-log.md` | Sprint history: what each iteration delivered |
```

New:
```
| File | Purpose |
|---|---|
| `requirements/` | Backlog: story cards + epics with stable IDs and proof obligations |
| `behavior-scenarios.md` | Behavior contracts: reusable scenario cards with stable IDs |
| `behavior-corpus.md` | Execution index: scenario → seam → cadence → command |
| `roadmap.md` | Sprint plan: ordered iterations with impacted scenarios |
| `iteration-log.md` | Sprint history: what each iteration delivered + scenarios added |
```

**Replace the Quality Gates section:**

Old:
```
Every evaluative gate uses parallel adversarial review (PAR):
- Pre-iteration scope review (citation + scope-creep + boxing-in look-ahead)
- Per-task spec-compliance review
- Per-task code-quality review with boxing-in check
- Per-sprint audit (deep new work + sweep whole product)
```

New:
```
Every evaluative gate uses parallel adversarial review (PAR):
- Pre-iteration scope review (citation + scope-creep + boxing-in + scenario coverage + story splitting)
- Pre-iteration sentinel corpus baseline
- Per-task spec-compliance review with evidence quality check
- Per-task code-quality review with boxing-in + corpus contribution check
- Post-iteration impacted + sentinel scenario runs
- Per-sprint audit (deep evidence + impacted behavior + sentinel corpus)
```

- [ ] **Step 2: Verify cross-references**

Read the modified SKILL.md and check that every referenced skill, artifact, and script exists:
- `extracting-requirements` — modified in Task 5
- `scoping-the-simplest-core` — modified in Task 6
- `running-an-iteration` — modified in Task 8
- `implementing-tasks` — modified in Task 12
- `auditing-progress` — modified in Task 14
- `behavior-scenarios.md`, `behavior-corpus.md` — created by extraction pipeline
- `skills/shared/behavior-evidence-formats.md` — created in Task 1
- `skills/shared/parallel-adversarial-review.md` — exists (unchanged)

- [ ] **Step 3: Commit**

```bash
git add skills/iterative-development/SKILL.md
git commit -m "feat: shift orchestrator completion gate to behavior evidence"
```

---

## Task 16: Add scenario validation script

**Files:**
- Create: `skills/extracting-requirements/scripts/validate_scenarios.py`

Validates the behavior-scenarios.md format and cross-checks story references against the requirements directory.

- [ ] **Step 1: Write the validation script**

Write `skills/extracting-requirements/scripts/validate_scenarios.py`:

```python
#!/usr/bin/env python3
"""Validate behavior-scenarios.md format and cross-references.

Usage: validate_scenarios.py <scenarios-file> <requirements-dir>

Checks:
- Every scenario has required fields (kind, proof seam, owning stories)
- All owning story references resolve to existing STORY-IDs
- Journey scenarios have steps (not empty)
- Scenario IDs are unique
- No UNRESOLVED() story references remain
"""
import re
import sys
from pathlib import Path


def load_story_ids(requirements_dir: Path) -> set[str]:
    """Collect all STORY-NNNN IDs from per-epic files."""
    ids: set[str] = set()
    for epic_file in requirements_dir.glob("EPIC-*.md"):
        for line in epic_file.read_text().splitlines():
            m = re.match(r"^## (STORY-\d+)", line)
            if m:
                ids.add(m.group(1))
    return ids


def validate(scenarios_path: Path, requirements_dir: Path) -> list[str]:
    """Validate scenarios file. Returns list of error strings."""
    errors: list[str] = []
    text = scenarios_path.read_text()
    lines = text.splitlines()

    known_stories = load_story_ids(requirements_dir)
    seen_ids: set[str] = set()

    current_id = None
    current_kind = None
    has_steps = False
    has_owning = False
    has_seam = False

    def flush():
        nonlocal current_id, current_kind, has_steps, has_owning, has_seam
        if current_id is None:
            return
        if not has_owning:
            errors.append(f"{current_id}: missing 'Owning stories' field")
        if not has_seam:
            errors.append(f"{current_id}: missing 'Proof seam' field")
        if current_kind == "journey" and not has_steps:
            errors.append(f"{current_id}: journey scenario has no steps")
        current_id = None
        current_kind = None
        has_steps = False
        has_owning = False
        has_seam = False

    for i, line in enumerate(lines, 1):
        # Scenario header
        id_match = re.match(r"^## (SCENARIO-\d+|JOURNEY-\d+)", line)
        if id_match:
            flush()
            current_id = id_match.group(1)
            if current_id in seen_ids:
                errors.append(f"line {i}: duplicate scenario ID {current_id}")
            seen_ids.add(current_id)

        if current_id:
            if line.startswith("**Kind:**"):
                current_kind = line.split(":**")[1].strip().lower()
            if line.startswith("**Proof seam:**"):
                has_seam = True
            if line.startswith("**Owning stories:**"):
                has_owning = True
                refs = line.split(":**")[1].strip()
                for ref in re.findall(r"STORY-\d+", refs):
                    if ref not in known_stories:
                        errors.append(f"{current_id}: references unknown {ref}")
                for unresolved in re.findall(r"UNRESOLVED\([^)]+\)", refs):
                    errors.append(f"{current_id}: has {unresolved}")
            if re.match(r"^\d+\.", line.strip()):
                has_steps = True

    flush()

    if not seen_ids:
        errors.append("no scenarios found in file")

    return errors


def main() -> int:
    if len(sys.argv) != 3:
        print(f"usage: {sys.argv[0]} <scenarios-file> <requirements-dir>",
              file=sys.stderr)
        return 2

    scenarios_path = Path(sys.argv[1])
    requirements_dir = Path(sys.argv[2])

    if not scenarios_path.exists():
        print(f"error: file not found: {scenarios_path}", file=sys.stderr)
        return 2
    if not requirements_dir.is_dir():
        print(f"error: directory not found: {requirements_dir}", file=sys.stderr)
        return 2

    errors = validate(scenarios_path, requirements_dir)
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        print(f"FAIL: {len(errors)} error(s)")
        return 1

    print("OK: scenarios valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Verify the script runs**

```bash
cd skills/extracting-requirements/scripts
echo '# Behavior Scenarios' > /tmp/test-empty-scenarios.md
mkdir -p /tmp/test-req-dir
python3 validate_scenarios.py /tmp/test-empty-scenarios.md /tmp/test-req-dir
```

Expected: `ERROR: no scenarios found in file` and exit code 1

- [ ] **Step 3: Commit**

```bash
git add skills/extracting-requirements/scripts/validate_scenarios.py
git commit -m "feat: add scenario validation script"
```

---

## Self-Review Checklist

### Spec coverage

Verified against the implementer spec `2026-04-11-iterative-development-behavior-evidence-redesign.md`:

| Spec section | Task |
|---|---|
| Extracting Requirements — emit proof obligations + scenarios | Tasks 2, 3, 4, 5 |
| Scoping — walking skeleton scenarios, story splitting | Task 6 |
| Running an Iteration — evidence tasks, sentinel baseline | Task 8 |
| Implementing Tasks — pre-flight mapping, corpus updates | Tasks 9, 12 |
| Spec-compliance reviewer — evidence quality | Task 10 |
| Code-quality reviewer — corpus contribution | Task 11 |
| Auditing Progress — three tiers | Tasks 13, 14 |
| Orchestrator — behavior evidence completion gate | Task 15 |
| Scenario card format | Task 1 |
| Behavior corpus index | Task 1 (format) + Task 5 (creation during extraction) |

Additional coverage from the review session (not in the implementer spec):

| Finding | Task |
|---|---|
| Journey-driven E2E as first-class extraction output | Task 2 (journey extraction variant) |
| Spec taxonomy → proof seam mapping | Task 1 (format reference) |
| Story splitting for heterogeneous-dependency ACs | Task 6 |
| Sentinel corpus baseline before iteration starts | Task 8 |

### Placeholder scan

No TBD, TODO, or "implement later" markers in any task step content.

### Type consistency

Cross-checked:
- `behavioral_impact` values: `none|local|cross-surface|journey` — consistent across formats reference (Task 1), extraction prompt (Task 2), story aggregation (Task 3)
- `proof_seam` values: `unit|integration|app-level|process-level|e2e` — consistent across formats reference (Task 1), extraction prompt (Task 2), reviewer prompts (Tasks 10, 11)
- Scenario kinds: `surface|journey|failure-recovery|contract` — consistent across formats reference (Task 1), extraction prompt (Task 2), aggregation script (Task 4)
- Scenario IDs: `SCENARIO-NNNN` for surface, `JOURNEY-NNNN` for journey — consistent across aggregation (Task 4), validation (Task 16), auditor prompt (Task 13)
- Behavior corpus fields: consistent between formats reference (Task 1), extraction SKILL (Task 5), running-an-iteration (Task 8)
