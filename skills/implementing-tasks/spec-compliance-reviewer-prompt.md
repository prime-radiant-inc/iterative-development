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
