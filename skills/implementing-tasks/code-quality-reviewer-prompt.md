# Code-Quality Reviewer Prompt Template

Use this template INSIDE the PAR wrapper when dispatching code-quality reviewers. This is Stage 2 of the two-stage review — it runs AFTER spec-compliance review passes.

```
[REVIEWER INSTRUCTIONS — insert inside PAR wrapper from skills/shared/par-reviewer-wrapper.md]

You are reviewing code quality and architectural soundness.

## What Was Implemented

[From the implementer's report — summary of what was built]

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

### Report Format

**Strengths:** [brief list]

**Issues:**
- Critical: [blocks correctness or downstream work — file:line refs]
- Serious: [significant quality problem — file:line refs]
- Minor: [style, naming — file:line refs]

**Boxing-In Assessment:** [CLEAR | RISK — with specific downstream iterations affected]

**Overall:** ✅ Approved | ❌ Changes needed
```
