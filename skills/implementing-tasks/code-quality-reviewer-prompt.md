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
- Is there dead code or unused imports?
- Are tests testing real behavior, not mock behavior?
- Does each file have one clear responsibility?

### Engineering Health
- **Abstraction justification:** Do the abstractions serve the product or
  just the test harness? An interface that exists solely for test injection,
  with no prospect of a second real implementation, is a design smell. Ask:
  could the behavior be tested without this indirection? If yes, the
  abstraction is not earning its place. This is a SERIOUS finding.
- **Platform fit:** Is the code working WITH the platform's idioms — native
  concurrency model, type system, standard patterns — or fighting them?
  Compiler suppressions, safety escape hatches, and manual reimplementation
  of platform-provided functionality are SERIOUS findings.
- **Navigability:** Can someone unfamiliar with the project find things by
  domain? If source files are dumped in a flat structure with no domain
  grouping, and the project has grown past the point where a directory
  listing reveals its shape, that is a SERIOUS finding.
- **Coordination creep:** Is a single file accumulating knowledge of every
  subsystem? If an orchestrator or controller is growing by accretion
  across iterations — becoming the place where everything gets wired
  together — that is a SERIOUS finding. Coordination should be decomposed
  along domain boundaries, not centralized.

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
