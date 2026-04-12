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
