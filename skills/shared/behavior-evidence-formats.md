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

## Test Infrastructure Checklist

Before the walking skeleton can pass its first journey scenario, the project needs a test harness. The walking skeleton's first task should be designing and building this harness. Answer these questions before writing harness code:

**Launch and teardown:**
- How does the test start the system under test?
- How does it shut it down cleanly after each scenario?
- Can scenarios run independently (no shared state between runs)?

**Input simulation:**
- How does the test simulate user actions (keyboard, mouse, voice, CLI, HTTP)?
- Can inputs be scripted and replayed deterministically?

**State observation:**
- How does the test observe the system's output or state changes?
- Can it query UI state, file system, database, or API responses?
- What is the observation latency (immediate, polling, event-driven)?

**External dependencies:**
- Does the system depend on OS services, network, hardware, or third-party APIs?
- Which dependencies can be substituted with fixtures in test?
- Which require real resources and why?

**Fixture strategy:**
- What test data does each scenario need (audio files, seed databases, config files)?
- Where do fixtures live and how are they versioned?

**Manual residuals:**
- What can't be automated and why?
- Is the manual portion documented as an explicit debt marker?

Document the answers in a test infrastructure section of the project's docs. The harness design becomes a reusable asset — later iterations extend it, they don't rebuild it.
