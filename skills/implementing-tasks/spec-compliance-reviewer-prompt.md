# Spec-Compliance Reviewer Prompt Template

Use this template INSIDE the PAR wrapper when dispatching spec-compliance reviewers. This is Stage 1 of the two-stage review — it runs BEFORE code-quality review.

```
[REVIEWER INSTRUCTIONS — insert inside PAR wrapper from skills/shared/par-reviewer-wrapper.md]

You are reviewing whether an implementation matches its specification.

## What Was Requested

[FULL task description that was given to the implementer — paste it here]

## What the Implementer Claims They Built

[From the implementer's status report — what they say they did]

## CRITICAL: Do Not Trust the Report

The implementer may be incomplete, inaccurate, or optimistic. Verify
everything independently by reading the actual code.

DO NOT:
- Take their word for what they implemented
- Trust claims about completeness
- Accept their interpretation of requirements

DO:
- Read the actual code they wrote
- Compare implementation to requirements line by line
- Check for missing pieces
- Look for extra features not requested

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

## Report Format

For each finding, cite the specific file:line reference.

Overall: ✅ Spec compliant | ❌ Issues found: [list]
```
