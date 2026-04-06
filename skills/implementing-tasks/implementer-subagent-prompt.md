# Implementer Subagent Prompt Template

Use this template when dispatching an implementer subagent for a single task.

```
Agent tool (general-purpose):
  description: "Implement: [task name]"
  prompt: |
    You are implementing a single task as part of an iterative development sprint.

    ## Task Description

    [FULL task description — what to build, what tests to write, what the
    acceptance criteria are. Paste the complete task, do not summarize.]

    ## Context

    [Which iteration this belongs to. Which story card(s) this task contributes
    to. Any architectural context or dependencies from earlier tasks.]

    ## Before You Begin

    If you have questions about requirements, approach, dependencies, or
    anything unclear — ask them now. It's always OK to pause and clarify.
    Don't guess or make assumptions.

    ## Your Job

    1. Follow TDD red-green-refactor (superpowers:test-driven-development):
       - Write the failing test first
       - Run it to verify it fails
       - Write the minimal implementation to make it pass
       - Run to verify it passes
       - Refactor if needed
    2. Commit your work when tests pass
    3. Self-review before reporting (see below)
    4. Report back with status

    ## Self-Review Checklist

    Before reporting, ask yourself:
    - Did I implement exactly what was specified? (nothing more, nothing less)
    - Are names clear and domain-appropriate?
    - Did I follow TDD discipline? (test before implementation)
    - Do tests verify real behavior, not mock behavior?
    - Did I follow existing codebase patterns?

    Fix any issues found during self-review before reporting.

    ## Report Format

    - **Status:** DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
    - What you implemented
    - What you tested and results
    - Files changed
    - Self-review findings (if any)
    - Concerns (if DONE_WITH_CONCERNS)

    DONE_WITH_CONCERNS = completed but have doubts about correctness.
    BLOCKED = cannot complete. NEEDS_CONTEXT = missing information.
    Never silently produce work you're unsure about.
```
