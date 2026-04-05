# Iterative Development Plugin — Design

**Date:** 2026-04-05
**Status:** Draft for review
**Pairs with:** `superpowers` plugin

## Executive summary

A new Claude Code plugin that provides an alternative implementation methodology to pair with `superpowers`. Instead of a single large upfront planning pass followed by a comprehensive implementation run, it extracts requirements once, defines a minimal walking skeleton, then loops: pick the next iteration, implement it end-to-end with TDD discipline, update tracking, repeat until an auditor confirms the product matches the spec.

The methodology is designed to scale to arbitrarily large specs (up to 50MB-plus prose dumps) without any single agent holding the entire spec in context, and to keep the product in a working, testable state at every iteration boundary.

## Motivation — why the current flow fails on complex work

The current superpowers flow is `brainstorming → writing-plans → subagent-driven-development` (or `executing-plans`). This produces excellent results for small-to-medium projects with bounded specs, but breaks down on large or comprehensive specs:

- **Heavy upfront planning**: the plan is written before any code runs, which locks in architectural decisions before learning has occurred.
- **Nothing works until the end**: the product is not demonstrably working until the last task is complete, so failures surface late.
- **Losing the plot**: as the plan and spec grow, no single agent can hold all the context. Later tasks drift, get stubbed, or silently drop requirements.
- **Scope creep in reverse**: AI agents under-build later tasks to fit context constraints, even when the spec required full implementation.
- **Gets worse with better specs**: the failure mode is counterintuitively amplified by spec quality — more detail means more context pressure.

The iterative methodology replaces "plan everything, then implement everything" with "extract requirements once, then loop through bounded iterations until the auditor is satisfied."

## Core principles

1. **Simplest core first.** The walking skeleton iteration exercises the end-to-end shape of the product with the thinnest possible slice. Every subsequent iteration adds the next most valuable capability.
2. **Don't box us in.** Iteration N's design must not block iterations N+1..N+3. Architectural commitments are deferred to the iteration that needs them.
3. **Strict artifact separation.** The plugin's internal documentation (`requirements-index.md`, `roadmap.md`, `iteration-log.md`) is kept in a dedicated directory and never modifies human-provided spec collateral.
4. **Scale to arbitrary spec size.** The extraction phase uses map-reduce over parallel subagents. No single agent ever reads the whole spec. A 50MB prose dump must not defeat the plugin.
5. **Always in a working state.** Every iteration ends with the product tested, committed, and releasable. Stopping mid-project at any iteration boundary leaves something better than the previous iteration.
6. **Audit every sprint.** An audit runs after every iteration as part of the planning cycle — not only at the end of the roadmap. The audit deep-checks the just-finished iteration's work and lightly sanity-sweeps the whole product for regressions. Completion is determined by the audit, not by the implementer or the roadmap self-declaring done.
7. **Parallel adversarial review.** Every evaluative gate dispatches two reviewer subagents in parallel, framed as competitors scoring on who finds the most serious or critical issues. The scoring is a psychological framing to pressure the reviewers to work hard — there is no actual point tracking or scoreboard. Aggregation takes the union of findings. This compensates for LLM reviewer sycophancy and exploits sampling variance for diversity.
8. **Evergreen state in artifacts.** All process state lives in `requirements-index.md`, `roadmap.md`, and `iteration-log.md`. Re-invoking `iterative-development` on an existing workspace resumes from where it left off. There is no ephemeral in-memory orchestrator state that would be lost across crashes or sessions.
9. **Autonomous by default.** The loop runs without human intervention. Human escalation is reserved for total catastrophe (the plugin cannot make progress at all). Requirements changes are signaled by human interrupt between iterations, not by polling or in-band prompts.

## Architecture overview

### Plugin skills

| Skill | Role |
|---|---|
| `iterative-development` | Orchestrator / entry point. Drives the lifecycle: extract → scope → loop (iteration → audit) → terminate. Resumable via re-invocation. |
| `extracting-requirements` | Scale layer. Reads arbitrary human spec collateral via parallel subagents, produces `requirements-index.md`. |
| `scoping-the-simplest-core` | Produces `roadmap.md`: walking-skeleton iteration + ordered follow-on iterations. |
| `running-an-iteration` | Drives one iteration: scope review → decomposition → task execution → wrap-up. Dispatches `implementing-tasks`. |
| `implementing-tasks` | The SDD fork. Takes a batch of tasks in memory, runs each through implementer + two-stage review loop. |
| `auditing-progress` | Per-sprint verification. Runs after every iteration: deep-checks the just-finished iteration's work and sanity-sweeps the whole product for regressions. Returns gaps as new backlog entries. |

### Internal artifacts (written by the plugin, never modifies human input)

All internal artifacts live in `docs/superpowers/iterations/` (sibling of `docs/superpowers/specs/` and `docs/superpowers/plans/`):

- **`requirements-index.md`** — the backlog. Every story card + epic extracted from human collateral, with stable global IDs and source citations.
- **`roadmap.md`** — the sprint plan. Walking-skeleton definition + ordered iteration list, each iteration referencing stories by ID.
- **`iteration-log.md`** — the sprint history. Append-only record of what each iteration delivered, lessons learned, roadmap revisions, scope-review outcomes.

### Human input artifacts (never modified)

Whatever the human brought in: one file, a directory tree, a 50MB prose dump, a mixed collection of markdown and diagrams. The plugin reads these, cites into them, and never writes to them.

## Artifacts in detail

### Story card format

Stories are the atomic testable unit of requirement. They live inside `requirements-index.md`.

```markdown
## STORY-0247

**Epic:** EPIC-014 — Keyboard-initiated dictation
**Title:** User starts dictation via global keyboard shortcut

**As a** user who prefers keyboard-driven workflows
**I want** to press a configurable global hotkey to start/stop dictation
**So that** I can dictate without touching the mouse

**Acceptance criteria:**
- AC-1: Pressing the configured hotkey while idle begins audio capture
- AC-2: Pressing the configured hotkey while recording stops capture
- AC-3: Hotkey is read from configuration at startup

**Sources:**
- `specs/domains/input.md:45-52`
- `specs/contracts/keyboard-interface.md:12-30`
- `test-vectors/input-vectors.md` — TV-003, TV-004

**Status:** pending | in_iteration:ITER-0012 | done:ITER-0012 | deferred
```

**Invariants:**
- Story IDs are **stable and global**. Once assigned, never renumbered. Deferred stories keep their IDs; new stories get new IDs.
- Every acceptance criterion must be directly testable.
- Every source reference includes a file path AND a line range (or named test vector).
- Status transitions are monotone except `pending → deferred` or `done → pending` (the latter only via audit reopening).

### Epic format

Epics are coarse groupings proposed by the extraction subagents during reading and consolidated in aggregation. They are not a human-designed taxonomy — they emerge from the spec content.

```markdown
## EPIC-014 — Keyboard-initiated dictation

**Summary:** All capabilities related to initiating, controlling, and terminating dictation via keyboard input.
**Stories:** STORY-0245, STORY-0246, STORY-0247, STORY-0248, STORY-0249
**Primary sources:** `specs/domains/input.md`, `specs/contracts/keyboard-interface.md`
**Status:** 0/5 done
```

### Roadmap format

`roadmap.md` contains the walking-skeleton definition and an ordered iteration list.

```markdown
# Roadmap

## Walking skeleton (ITER-0000)

**Intent:** The thinnest end-to-end slice that exercises the full product shape.
**Design rationale:** [brief description of which stories were chosen and why they form a cohesive end-to-end path]
**Stories committed:**
- STORY-0001 (EPIC-001)
- STORY-0042 (EPIC-003)
- STORY-0156 (EPIC-008)
**Status:** done | in_progress | pending

## Iteration list

### ITER-0001 — [descriptive name]
**Stories:** STORY-0002, STORY-0003, STORY-0004
**Rationale:** [why these, why now]
**Status:** pending
**Look-ahead check:** [results of boxing-in review]

### ITER-0002 — ...
```

### Iteration log format

`iteration-log.md` is append-only. Each iteration gets an entry.

```markdown
# Iteration Log

## ITER-0000 — Walking skeleton
**Completed:** 2026-04-07
**Stories delivered:** STORY-0001, STORY-0042, STORY-0156
**Tasks executed:** 7
**Summary:** [short paragraph]
**Learnings:** [anything that should influence later iterations]
**Roadmap revisions:** [if any]

## ITER-0001 — ...
```

## Skills in detail

### `iterative-development` (orchestrator)

**Trigger:** user invokes the plugin on a directory containing human spec collateral. Re-invocation resumes from existing state.

**Behavior:**
1. Check for existing `docs/superpowers/iterations/` — if present and non-empty, resume from that state. If absent, bootstrap fresh.
2. If bootstrap needed: invoke `extracting-requirements` → invoke `scoping-the-simplest-core`.
3. **Check for human interrupt signal** (see "Human interrupt protocol" below). If the human has signaled a requirements change, invoke `extracting-requirements` in incremental mode on the new/changed spec files and rebuild the roadmap before proceeding.
4. Loop (per-iteration):
   - Invoke `running-an-iteration` (picks next pending iteration, runs it to completion)
   - Invoke `auditing-progress` (deep-checks new work + light sanity sweep of whole product)
   - If audit finds gaps: append gap stories to backlog, revise roadmap accordingly
   - If `roadmap.md` still has pending iterations: loop back to step 3
5. When roadmap is empty AND the last audit was clean: terminate.

The orchestrator is thin. Each phase is independently invokable — users can run `extracting-requirements` alone, or kick off a single `running-an-iteration`, without going through the orchestrator. Running the orchestrator again on an existing workspace resumes cleanly from the artifacts; there is no ephemeral state to recover.

**Resumption model:** the command "continue iterative development with the existing plan" always works. All state lives in the three artifact files. If the orchestrator crashes mid-iteration, the partially-completed iteration's git commits are preserved; on resume, the orchestrator picks up at the next un-started iteration (the in-progress iteration is either finished on resume or retried from its last committed state).

### `extracting-requirements`

**Input:** path to human spec collateral (file, directory, or explicit file list).
**Output:** `docs/superpowers/iterations/requirements-index.md`.

**Process:**

1. **Inventory.** Main agent enumerates files in the collateral (glob + file sizes). For each file, reads only enough to generate a one-line summary (title or first heading) — never the full contents. Produces a manifest.

2. **Chunking.** Main agent decides chunking per file based on size:
   - < 4K tokens: whole-file chunk
   - 4K–30K tokens: split by top-level headings
   - \> 30K tokens: split by second-level headings, with token-budget ceiling
   - Binary / unreadable files: skipped, logged for human review

3. **Parallel extraction.** Main agent dispatches extraction subagents in parallel, each with one or more chunks. Parallelism level is a main-agent judgment call based on spec size, model cost, and rate-limit budget. Each subagent:
   - Reads only its assigned chunks
   - Emits structured story-card proposals (YAML or JSON) with acceptance criteria and precise line-range citations
   - Proposes epic groupings inline (just theme names, no ID assignment)
   - Does NOT attempt global dedup or ID assignment

4. **Aggregation (reduce).** Main agent dispatches an aggregation subagent (or runs aggregation inline if results fit). Aggregation:
   - Dedupes stories by title exact-match and AC-overlap similarity
   - Merges epic candidates with matching themes
   - Assigns stable global IDs (STORY-NNNN, EPIC-NNN) in deterministic order
   - Writes `requirements-index.md`

5. **Hierarchical reduce (if needed).** For very large specs where a single aggregation pass exceeds context, the main agent partitions aggregated results and runs aggregation subagents in a second tier. Repeats until a single index is produced.

6. **Huge-spec decomposition (> 1M tokens).** Before chunking, main agent dispatches a decomposition subagent that identifies natural sub-project boundaries in the collateral (e.g., "Word", "Excel", "PowerPoint" within an MS Office spec). Each sub-project runs its own extraction pipeline. Results merge at a final aggregation tier.

7. **Incremental re-extraction.** If new spec files appear mid-project, the skill can be re-invoked with just the new files. New story cards get new IDs; existing IDs are preserved.

**Key invariant:** the main agent never reads raw spec contents beyond the inventory phase. Subagents see their chunks; the main agent sees the inventory and the aggregated index.

### `scoping-the-simplest-core`

**Input:** `requirements-index.md`.
**Output:** `docs/superpowers/iterations/roadmap.md`.

**Process:**

1. Read `requirements-index.md` — specifically the epic summaries and story titles, not full story contents. Dip into story ACs only when selecting.

2. **Define the walking-skeleton iteration (ITER-0000).** Select a small cohesive set of stories — chosen from as many distinct epics as possible — that together exercise the end-to-end shape of the product. Selection rule: "if someone ran just these stories, they should see a demo that proves the product exists and works."

3. **Order remaining stories into iterations.** Each iteration is a "sprint's worth" of cohesive work. Project-shape dependent — no hardcoded iteration count or story count per iteration.

4. **Run pre-commit scope reviews.** All three reviews use **parallel adversarial review** (see dedicated section) — two competing reviewer subagents per check:
   - **Citation check:** every iteration's scope list cites only valid STORY-IDs from the index.
   - **Adversarial scope check:** reviewers argue against any bundled scope ("could this be split?", "is the coupling real?").
   - **Boxing-in look-ahead:** reviewers examine ITER-0000 design assumptions against ITER-0001..ITER-0003. Any downstream iteration that would be blocked by ITER-0000's design is flagged.

5. **Revise and re-review until all checks pass.** Write `roadmap.md`.

### `running-an-iteration`

**Input:** `roadmap.md` (and the iteration to run — next pending by default, or explicitly named).
**Output:** updated `roadmap.md`, updated `requirements-index.md` (story status flips), appended `iteration-log.md` entry. Does NOT invoke `auditing-progress` itself; that's the orchestrator's responsibility after this skill returns.

**Process:**

1. **Pick next iteration** from `roadmap.md`.

2. **Load scope context.** Read the cited stories and their sources from `requirements-index.md`. Identify the acceptance criteria that define iteration success.

3. **Pre-iteration scope review** (new in this plugin, not present in SDD). All three checks use **parallel adversarial review** — two competing reviewer subagents per check:
   - Citation check: scope references only valid story IDs
   - Adversarial scope check: reviewers argue "does this iteration try to do too much?"
   - Boxing-in look-ahead: reviewers examine the iteration's planned design against the next 3 pending iterations; flag coupling or commitment that would block them
   - Iterate with revisions until all checks pass

4. **Decompose into tasks.** Main agent breaks the iteration scope into TDD-sized tasks (each task = failing test → implementation → passing test → commit). Tasks are inline in memory — no separate plan file. **Iteration granularity is judgment-based, not defaulted** — story counts per iteration vary widely based on project shape. The scoping subagent exercises judgment; the orchestrator does not enforce a fixed count.

5. **Dispatch `implementing-tasks`.** Pass the task list and iteration context. The task-runner executes each task through implementer + spec-reviewer + code-quality-reviewer, with re-dispatch loops on failures.

6. **Wrap up:**
   - Verify all iteration stories' ACs pass (implementer-side sanity check; the audit that follows will verify independently)
   - Mark stories `done:ITER-NNNN` in `requirements-index.md`
   - Update iteration status in `roadmap.md`
   - Append a structured entry to `iteration-log.md`: stories delivered, task count, learnings, any roadmap revisions proposed

After this skill returns, the orchestrator invokes `auditing-progress` before picking the next iteration.

### `implementing-tasks` (the SDD fork)

**Input:** an in-memory batch of tasks + iteration context (cited stories, ACs, source citations).
**Output:** completed work, commits, review sign-off per task. Returns per-task status to caller.

**Relationship to `superpowers:subagent-driven-development`:** this is a fork. Same quality discipline, different entry/exit.

**What's stripped:**
- "Read plan file + extract all tasks" — tasks come directly from the caller in memory
- Final end-of-plan code reviewer (entire-implementation review) — replaced by the periodic audit in `auditing-progress`
- Upstream dependency on `superpowers:writing-plans` — no separate plan file exists
- Downstream handoff to `superpowers:finishing-a-development-branch` — iterations don't finish branches; that's a project-level concern

**What's kept unchanged:**
- Implementer subagent prompt template (TDD discipline, self-review, four-status reporting)
- Two-stage review structure (spec compliance before code quality)
- Review re-dispatch loop (reviewer finds issues → implementer fixes → reviewer re-reviews)
- Model selection rules (cheap for mechanical, standard for integration, capable for judgment)
- Escalation pattern (BLOCKED / NEEDS_CONTEXT / DONE_WITH_CONCERNS)

**What's adapted:**
- **Spec-compliance reviewer input:** receives the iteration scope (cited stories + ACs) inline, not a plan file path. Reviewer verifies the task achieves the cited stories, nothing more, nothing less.
- **Code-quality reviewer prompt:** adds a **boxing-in check** question: "Given the next 3 pending roadmap iterations, does this task introduce coupling, hardcoding, or structural commitments that would block any of them?" Reviewer responds with explicit yes/no + rationale.
- **Both reviewer stages are dispatched as parallel adversarial pairs** (see dedicated section). Each reviewer prompt gets a competitive-framing wrapper added. Per task, this means two spec-compliance reviewers in parallel, then two code-quality reviewers in parallel — four reviewer dispatches per pre-issues pass. Re-review after implementer fixes uses a fresh pair with no state carry-over.

### `auditing-progress`

**Input:** `requirements-index.md` + the just-finished iteration's ID (from `iteration-log.md`) + current product state.
**Output:** list of gaps (REQ-IDs whose ACs don't actually pass) and unrequested features.

Runs **after every iteration**, invoked by the orchestrator. Uses a **hybrid scope**: deep-checks the stories the just-finished iteration claimed to deliver, then lightly sanity-sweeps the whole product for regressions.

**Process:**

1. **Partition the audit work into two tiers:**
   - **Deep tier:** stories marked `done:ITER-<current>` — the ones this iteration just delivered. Audit every AC thoroughly, run tests, read code, verify claims.
   - **Sweep tier:** all other stories previously marked `done`. Light sanity check — run test suites, spot-check that the story's ACs are still being exercised, look for obvious regressions. Not a full re-verification.

2. **Dispatch parallel adversarial pairs.** Each partition (deep and sweep) is audited by a parallel adversarial auditor pair. For large backlogs, the main agent may further partition by epic and dispatch multiple paired teams, at its judgment.

3. **Each auditor subagent, per assigned story:**
   - Reads the story's acceptance criteria and cited sources
   - Reads the tests and code that claim to implement those ACs
   - Runs the tests (via provided harness)
   - For deep-tier: verifies each AC is actually met, flags any partial/missing/ambiguous
   - For sweep-tier: verifies the story's tests still pass and no obvious regression surface

4. **Unrequested feature scan.** Each auditor also scans the iteration's diff for features, flags, or commands that don't map back to any story. These are reported separately.

5. **Aggregation.** Main agent collects auditor reports:
   - **Gaps on the just-finished iteration** → append to backlog as new stories (or flip existing stories from `done:ITER-<n>` back to `pending`), revise roadmap to insert a follow-up iteration
   - **Regressions in previously-done stories** → same treatment: reopen or add stories to backlog
   - **Unrequested features** → append to backlog as removal tasks
   - **Pass** → story confirmed done; orchestrator proceeds to next iteration

6. **Return control to the orchestrator.** The orchestrator uses the audit result to decide whether to rebuild the roadmap (if gaps found) or proceed to the next pending iteration (if clean).

## End-to-end flow

```
┌───────────────────────────────────────────────┐
│        human spec collateral                  │
│     (any shape, any size, read-only)          │
└───────────────┬───────────────────────────────┘
                │
                ▼
  ┌─────────────────────────────────────┐
  │ extracting-requirements             │  map-reduce over chunks
  │  - inventory                        │  parallel extraction subagents
  │  - chunking                         │  hierarchical aggregation for huge specs
  │  - parallel extraction              │  main agent never reads raw spec
  │  - aggregation (+ hierarchical)     │
  └─────────────────┬───────────────────┘
                    │
                    ▼
      ┌──────────────────────────────┐
      │  requirements-index.md       │  (backlog: stories + epics, stable IDs)
      └─────────────────┬────────────┘
                        │
                        ▼
  ┌─────────────────────────────────────┐
  │ scoping-the-simplest-core           │  walking-skeleton selection
  │  - citation check (PAR)             │  boxing-in look-ahead (PAR)
  │  - adversarial scope check (PAR)    │
  └─────────────────┬───────────────────┘
                    │
                    ▼
        ┌───────────────────────────┐
        │   roadmap.md              │  (ordered iterations + walking skeleton)
        └─────────────┬─────────────┘
                      │
                      ▼
          ┌───────── interrupt check? ◄──── human signals requirements change
          │                                 (out-of-band, between iterations)
          ▼
  ┌──────────────────────┐
  │ running-an-iteration │  ◄────────────────────┐
  │  - scope review (PAR)│                       │
  │  - decompose tasks   │                       │
  │  - dispatch fork     │                       │
  │  - wrap-up           │                       │
  └──────────┬───────────┘                       │
             │                                   │
             ▼                                   │
  ┌──────────────────────┐                       │
  │  implementing-tasks  │                       │
  │      (SDD fork)      │                       │
  │  - implementer       │                       │
  │  - spec review (PAR) │                       │
  │  - quality rev (PAR) │                       │
  │  - boxing-in check   │                       │
  │  - re-dispatch loop  │                       │
  └──────────┬───────────┘                       │
             │                                   │
             ▼                                   │
  ┌──────────────────────────────┐               │
  │ auditing-progress            │               │
  │  (runs after EVERY iteration)│               │
  │  - deep: new work            │               │
  │  - sweep: whole product      │               │
  │  - paired auditors (PAR)     │               │
  │  - gaps + unrequested feats  │               │
  └──────────┬───────────────────┘               │
             │                                   │
       gaps found?                               │
         │   │                                   │
     yes │   │ no                                │
         │   │                                   │
         │   ▼                                   │
         │   more iterations? ──yes──────────────┤
         │       │ no                            │
         │       │ (roadmap empty AND audit      │
         │       │  clean)                       │
         │       ▼                               │
         │   [terminate]                         │
         │                                       │
         └──► append gaps to backlog, ───────────┘
              revise roadmap, loop
```

## Quality gates

The methodology has three distinct quality gates, each with a different purpose and scope:

### Gate 1: Pre-iteration scope review (new in this plugin)

**When:** before `implementing-tasks` is dispatched for an iteration.
**What:** citation integrity + scope-creep prevention + boxing-in look-ahead.
**Who:** scope reviewers, dispatched as a **parallel adversarial pair** (see next section).
**Pass criteria:** every capability in the iteration cites a valid story ID; scope is cohesive and not bundled; next 3 pending iterations are not blocked by this iteration's planned design.

### Gate 2: Per-task two-stage review (from SDD, adapted)

**When:** after each task inside `implementing-tasks`.
**What:** Stage 1 — spec compliance (does the implementation match the iteration scope it was given?). Stage 2 — code quality + boxing-in check.
**Who:** two sequential review stages, **each dispatched as a parallel adversarial pair**. Four reviewer calls per task before any re-review loops.
**Pass criteria:** aggregated findings from both stages are empty (or fixed). Failures loop back to the implementer; re-review uses fresh pairs.

### Gate 3: Per-sprint audit (new in this plugin)

**When:** after **every** iteration, as part of the planning cycle before the next iteration starts.
**What:** **hybrid scope** — deep verification of the just-finished iteration's claimed work (every AC thoroughly checked) PLUS a lightweight sanity sweep over the whole product (test suites still pass, no obvious regressions). Also scans the iteration's diff for unrequested features.
**Who:** auditors partitioned into two tiers (deep + sweep), **each partition audited by a parallel adversarial pair**. For large backlogs the sweep tier may be further partitioned by epic with multiple paired teams. Main agent chooses partition count at its judgment.
**Pass criteria:** zero gaps in the just-finished iteration's claimed work, zero new regressions in previously-done stories, zero unrequested features in the iteration's diff.

Each gate catches a different class of problem:
- Gate 1 catches scope-creep and architectural boxing-in **before** code is written.
- Gate 2 catches per-task correctness and quality **during** implementation.
- Gate 3 catches drift, missing requirements, regressions, and unrequested features **after each iteration** — not just at the end.

## Parallel adversarial review

Every evaluative gate in this plugin — scope reviews, per-task reviews, audits — dispatches reviewers as **parallel adversarial pairs**: two reviewer subagents running the same check against the same inputs in parallel, framed as competitors scoring on issue discovery.

### The pattern

1. **Dispatch two reviewer subagents simultaneously** with identical inputs. Neither sees the other's work.
2. **Each reviewer receives competitive framing** in its prompt:
   - "You are Reviewer [A|B]. A parallel reviewer is evaluating the same work right now."
   - "Scoring: whoever finds the greatest number of serious or critical issues wins 5 points."
   - "Findings must be real and justified with file:line references. Nitpicks don't count toward scoring."
   - "Be thorough — your competitor is being thorough too."
3. **Both reviewers return independently.**
4. **Main agent aggregates findings:**
   - **Same issue found by both** → one finding, high confidence
   - **Issue found by only one** → separate finding, lower confidence but still actionable
   - **Severity disagreement** → take the more severe assessment; flag strongly contested cases for human review
5. **Aggregated findings pass to the implementer** (or the roadmap author for scope reviews, or the backlog for audits).
6. **Re-review uses a fresh parallel adversarial pair.** No state carries between review iterations.

### Why it works

LLM reviewers default to shallow, sycophantic approval when the work looks reasonable. Competitive framing plus a concrete scoring rule creates pressure to be thorough. Two reviewers also provide diversity through sampling variance — they independently find different issues that the aggregation step unions.

**The scoring is a psychological trick.** The "5 points" and "whoever finds the most" framing is purely prompt-level. There is no actual point tracking, no scoreboard, no persistent competitive state across reviews. The purpose is solely to pressure the reviewer agents to work hard against the current task — nothing more. Do not implement scoring infrastructure.

### Where it applies

| Gate | Reviewer role | Dispatched as pair? |
|---|---|---|
| Pre-iteration scope review | Scope reviewer | Yes |
| Per-task spec compliance | Spec-compliance reviewer | Yes |
| Per-task code quality | Code-quality reviewer | Yes |
| Terminal audit | Auditor | Yes (per partition) |

### Where it does NOT apply

- **Implementer subagents** — they're doers, not evaluators
- **Implementer self-review** — internal discipline, part of the implementer's own work
- **Extraction subagents** — they read spec chunks, they don't evaluate
- **Aggregation/dedup subagents** — mechanical merging, not evaluative
- **Decomposition subagents** (huge-spec sub-project identification) — structural, not evaluative

### Cost implication

Per task, the reviewer cost is 2× spec-compliance + 2× code-quality = 4 reviewer dispatches before any re-review loops. This is significant overhead relative to the implementer's cost. The trade-off: evaluative gates are where drift and scope-creep get caught. False negatives here propagate into wasted iterations downstream, which costs more than the review overhead.

**PAR is always-on. There is no per-gate opt-out.** Every evaluative gate in the plugin uses PAR unconditionally.

### Severity disagreement resolution

When the two paired reviewers assign different severity to the same finding (e.g., Reviewer A says "critical," Reviewer B says "minor"), the aggregator **always takes the more severe assessment and always fixes it**. No threshold, no escalation to human, no negotiation.

## Human interrupt protocol

The plugin runs as an autonomous loop. The only way the human injects new information mid-run is by interrupting the orchestrator between iterations.

**Model: out-of-band signaling.**

- The human does NOT submit spec changes through a structured interface, checkpoint prompt, or polled file watcher.
- The human types the update into the chat session running the orchestrator ("we dropped the keyboard hotkey feature," "add a new domain for X," "the accessibility contract changed, re-read `specs/contracts/accessibility-api.md`").
- The orchestrator notices the interrupt at the **next iteration boundary** — specifically, after the current iteration's audit completes and before the next `running-an-iteration` is dispatched.
- At that point, the orchestrator invokes `extracting-requirements` in incremental mode on the changed spec files, merges the new/revised story cards into `requirements-index.md`, revises `roadmap.md` if the changes invalidate downstream iterations, and resumes.

**Guarantees:**
- Changes during the middle of an iteration do NOT disrupt the in-progress work. The current iteration completes, then the interrupt is processed.
- The orchestrator never silently drops an interrupt. If an interrupt cannot be fully processed (e.g., the human's statement is ambiguous), the orchestrator asks for clarification *before* resuming iteration work.
- Existing story IDs are preserved across re-extraction. Removed stories flip to `deferred` (not deleted). Revised stories get an updated revision marker but keep their ID.

**What does NOT trigger interrupt processing:**
- The orchestrator does not poll the filesystem for spec changes on its own.
- The orchestrator does not ask "anything to change?" between iterations.
- Human presence is not required at iteration boundaries; interrupts are opportunistic.

## Scale strategy

Spec size drives the extraction strategy:

| Spec size | Strategy |
|---|---|
| Single file, < ~10K tokens | One extraction subagent, no aggregation. |
| Multiple files, ~10K–100K tokens | One extraction subagent per file in parallel, single aggregation pass. |
| Large (100K–1M tokens) | Chunk by file AND by section, parallel extraction, single or hierarchical aggregation. |
| Huge (> 1M tokens) | Decomposition pass identifies sub-projects first; each sub-project runs its own extraction pipeline; final aggregation tier merges. |

**Invariant across all sizes:** the main agent never reads raw spec contents after the inventory phase. It orchestrates and reads only indices and aggregated results.

The audit phase scales the same way: for large backlogs, auditors partition by epic and run in parallel.

## Termination logic

The plugin is a **guarded Ralph Wiggum loop** — autonomous recursion with structured gates as the termination oracle. The audit runs after every iteration, so termination is simply "roadmap empty AND the most recent audit was clean."

```python
while True:
    check_for_human_interrupt()  # non-blocking; processes pending spec changes if any

    if not roadmap.has_pending_iterations():
        if last_audit_clean:
            break  # true completion
        else:
            # audit found gaps which added new iterations; continue
            pass

    run_next_iteration()          # running-an-iteration
    audit_result = run_audit()    # auditing-progress, per-sprint

    if audit_result.gaps or audit_result.unrequested_features:
        add_gaps_to_backlog(audit_result)
        revise_roadmap()
        last_audit_clean = False
    else:
        last_audit_clean = True

emit_completion_summary()
```

The loop is bounded by the auditor's judgment, not by the implementer's self-declaration or the roadmap's finiteness. Gaps found by the audit become new iterations. Only a clean audit on an empty roadmap terminates the loop.

**Autonomy guarantee.** The only reason the loop pauses is a total catastrophic failure — the plugin cannot make any forward progress at all. Ambiguity, difficulty, or merely slow progress never triggers human escalation. The loop does not prompt the human "should I continue?" between iterations. If a reviewer or auditor finds issues, those become new work; they do not interrupt autonomy.

## Relationship to superpowers

**Invoked at runtime (the plugin depends on these):**
- `superpowers:test-driven-development` — invoked inside every implementer task
- `superpowers:brainstorming` — optional upstream, used when the human needs help crafting the initial spec
- `superpowers:requesting-code-review` — review prompt templates for reviewer subagents
- `superpowers:verification-before-completion` — applied by auditor subagents
- `superpowers:systematic-debugging` — applied by implementer subagents when stuck

**Forked at source-code level (not invoked at runtime):**
- `superpowers:subagent-driven-development` → `implementing-tasks`. The fork strips the plan-file dependency and the final end-of-plan reviewer, keeps the implementer + two-stage review loop, and adds a boxing-in check to the code-quality reviewer.

**Deliberately not used:**
- `superpowers:writing-plans` — replaced by inline iteration decomposition; no separate plan file exists
- `superpowers:executing-plans` — replaced by `running-an-iteration` + `implementing-tasks`
- `superpowers:using-git-worktrees` — the plugin does not manage worktrees; user sets up isolation if desired

**Positioning:** the iterative-development plugin is an alternative to `writing-plans → subagent-driven-development / executing-plans`. A user picks between the current flow (best for small-to-medium projects with bounded specs) and the iterative flow (best for large, comprehensive, or ambiguous specs).

## What's out of scope for this design

- **Replacing `superpowers:brainstorming`.** The iterative flow still expects a spec (of any shape) as input. How that spec gets created is upstream and unchanged.
- **Worktree management.** The user creates a worktree if they want one, before invoking the plugin.
- **CI/CD integration.** The plugin writes commits; it does not push, open PRs, or trigger pipelines. That's user-initiated after termination.
- **Cross-project orchestration.** The plugin operates on one project at a time. Multi-repo coordination is not addressed.

## Open design decisions (to be resolved during implementation planning)

These are the questions that remain after the design phase. Everything else has been locked in above.

1. **Roadmap revision mechanism after audit.** When the audit finds gaps and the roadmap needs to be revised, what's the formal mechanism? Inline edit by the orchestrator, a dedicated `revising-the-roadmap` step, or re-run `scoping-the-simplest-core` on the updated backlog? Implementation-dependent choice.

2. **Deduplication thresholds in extraction.** AC-overlap similarity threshold for merging stories during aggregation. Value unknown — to be tuned during implementation.

3. **Walking-skeleton identification heuristic.** Beyond "cross-cut multiple epics with happy-path stories", is there a more formal selection rule the scoping subagent should follow? To be explored during implementation.

## Resolved design decisions (for the record)

The following were raised and resolved during the brainstorming phase. Recorded here so the implementation planner does not re-open them.

- **Skill name for the SDD fork:** `implementing-tasks` (was placeholder `running-reviewed-tasks`).
- **Audit skill name:** `auditing-progress` (was `auditing-for-completion`, misleading once audit moved to per-sprint).
- **Iteration granularity defaults:** none — story sizes vary wildly, the scoping subagent uses judgment, no hardcoded count.
- **Parallel subagent cost/rate-limit ceiling:** main agent uses judgment; no hardcoded ceiling.
- **Resumption after interruption:** all state lives in the three artifact files; re-invoking the orchestrator on an existing workspace resumes cleanly. The command "continue iterative development with the existing plan" always works. No separate resumption mechanism.
- **Audit frequency:** after every iteration, as part of the planning cycle. Not terminal-only.
- **Incremental re-extraction UX:** the human interrupts the orchestrator (out-of-band); orchestrator processes at the next iteration boundary. No polling, no explicit `--incremental` flag exposed to the user.
- **PAR per-gate opt-out:** none. PAR is always-on for all evaluative gates.
- **PAR severity disagreement:** always take the more severe assessment, always fix it. No threshold, no escalation.
- **PAR model diversity:** single-model for now (sampling variance provides diversity). Multi-model is future work.
- **PAR scoring:** the "5-point" scoring is a psychological framing only. No point tracking, no scoreboard, no persistent competitive state. Do not build scoring infrastructure.
- **PAR false positive handling:** no special mechanism. Aggregation + justification requirement (file:line references) + implementer pushback during re-review handle the edge case.
- **Escalation to human:** only on total catastrophic failure where the plugin cannot make any forward progress. The loop is autonomous otherwise.
- **Human interrupt protocol:** out-of-band — human types into chat, orchestrator processes between iterations. Orchestrator does not poll, does not ask between iterations, does not wait for human presence.
