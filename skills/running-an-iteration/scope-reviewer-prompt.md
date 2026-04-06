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
