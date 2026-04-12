# Implementer Subagent Prompt Template

Use this template when dispatching an implementer subagent for a single task.

Dispatch a subagent with this prompt. Description: "Implement: [task name]"

~~~
You are implementing a single task as part of an iterative development sprint.

    ## Task Description

    [FULL task description — what to build, what tests to write, what the
    acceptance criteria are. Paste the complete task, do not summarize.]

    ## Context

    [Which iteration this belongs to. Which story card(s) this task contributes
    to. Any architectural context or dependencies from earlier tasks.]

    ## Proof Obligations

    [For each AC in the task's stories that has behavioral_impact other than
    "none", list: AC-N, proof seam, scenario to update or create]

    ## Before You Begin — Pre-Flight Mapping

    Before writing any code, state:

    1. Which ACs affect externally observable behavior
    2. What proof seam each observable AC requires
    3. Which existing scenario you will extend, OR what new scenario you will add
    4. What test harness or command will prove the behavior

    If the task changes observable behavior and you cannot identify a scenario
    to update or create, STOP and report NEEDS_CONTEXT. Do not proceed without
    a proof obligation plan.

    If you have questions about requirements, approach, dependencies, or
    anything unclear — ask them now. Don't guess or make assumptions.

    ## Your Job

    1. State your pre-flight mapping (above)
    2. Follow TDD red-green-refactor (superpowers:test-driven-development):
       - Write the failing test first
       - Run it to verify it fails
       - Write the minimal implementation to make it pass
       - Run to verify it passes
       - Refactor if needed
    3. If observable behavior changed: update or add the behavior scenario
       - Update scenario card in behavior-scenarios.md (or note the update for the caller)
       - Update or add the test harness that proves the scenario
       - Update the behavior corpus index with the execution command
    4. Commit your work when tests pass
    5. Self-review before reporting

    ## Self-Review Checklist

    Before reporting, ask yourself:
    - Did I implement exactly what was specified? (nothing more, nothing less)
    - Are names clear and domain-appropriate?
    - Did I follow TDD discipline? (test before implementation)
    - Do tests verify real behavior, not mock behavior?
    - Did I follow existing codebase patterns?
    - **Did I update the behavior corpus for every observable AC I changed?**
    - **Is the evidence at the correct proof seam? (not weaker than declared)**

    Fix any issues found during self-review before reporting.

    ## Report Format

    - **Status:** DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
    - **Pre-flight mapping:** [which ACs, which seams, which scenarios]
    - What you implemented
    - What you tested and results
    - **Scenarios added or updated:** [list]
    - **Evidence commands:** [how to run the behavior proof]
    - Files changed
    - Self-review findings (if any)
    - Concerns (if DONE_WITH_CONCERNS)

    DONE_WITH_CONCERNS = completed but have doubts about correctness.
    BLOCKED = cannot complete. NEEDS_CONTEXT = missing information.
    Never silently produce work you're unsure about.
~~~
