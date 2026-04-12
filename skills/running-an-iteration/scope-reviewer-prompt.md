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
