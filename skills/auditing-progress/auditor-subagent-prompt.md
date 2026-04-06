# Auditor Subagent Prompt Template

Use this template when dispatching auditor subagents inside the PAR wrapper. Fill in the bracketed values.

```
[REVIEWER INSTRUCTIONS — insert inside PAR wrapper from skills/shared/par-reviewer-wrapper.md]

You are auditing a just-completed iteration's work against its story
acceptance criteria.

## Stories to Audit

[For each story marked done:ITER-<current>, paste the story card including
all acceptance criteria and source citations]

## Your Job

For each story:
1. Read the acceptance criteria
2. Find the tests and code that claim to implement them
3. Run the tests
4. Verify each AC is actually met — not just that tests pass, but that
   the tests actually TEST what the AC requires
5. Flag any AC that is NOT met with:
   - The story ID and AC number
   - What the AC requires
   - What the code/tests actually do
   - Why there is a gap

Also scan the iteration's git diff for:
- Features, flags, or commands that don't map to any story (unrequested work)
- Commented-out code or debug artifacts left behind

## Report Format

For each story:
- STORY-NNNN: [PASS | FAIL]
  - AC-1: [PASS | FAIL — explanation if fail]
  - AC-2: [PASS | FAIL — explanation if fail]

Unrequested features found: [list or "none"]

Overall: [CLEAN | GAPS FOUND]
```
