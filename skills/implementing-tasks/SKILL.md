---
name: implementing-tasks
description: Use when executing a batch of TDD-sized tasks inside a running-an-iteration call — dispatches an implementer subagent per task following red-green-refactor discipline and returns per-task completion status.
---

# Implementing Tasks

## Overview

Takes an in-memory batch of TDD-sized tasks and executes each through an implementer subagent following red-green-refactor discipline. This is a fork of `superpowers:subagent-driven-development` with the plan-file reading phase stripped and the final end-of-plan reviewer removed.

**This is Plan 1 — walking skeleton implementation. The two-stage review (spec compliance + code quality), review re-dispatch loop, boxing-in check, parallel adversarial review wrappers, and model selection rules are NOT yet implemented and will be added in later plans.**

## When to Use

Invoked by `running-an-iteration` with a list of tasks. Each task is a complete TDD cycle (failing test → implementation → passing test → commit). Tasks are passed in memory, not via a file.

## Walking Skeleton Behavior (Plan 1)

For each task in the provided list:

1. Dispatch an implementer subagent with:
   - The task description and context (the story card(s) the task contributes to)
   - Instructions to follow TDD red-green-refactor (`superpowers:test-driven-development`)
   - Instructions to commit the work when tests pass
   - Instructions to report back with status DONE / DONE_WITH_CONCERNS / BLOCKED / NEEDS_CONTEXT

2. Wait for the subagent to complete. Do not run tasks in parallel.

3. Handle the returned status:
   - DONE: record the task as complete, move to the next
   - DONE_WITH_CONCERNS: record the concerns, move to the next (Plan 1 does not block on concerns)
   - BLOCKED or NEEDS_CONTEXT: return control to the caller with the blocker details. The caller decides whether to provide more context and re-dispatch, or escalate

4. After all tasks complete, return a per-task result list to the caller.

**No review dispatch in Plan 1.** The implementer's self-review is the only quality gate at this point. Two-stage review and PAR wrappers come in later plans.

## Quick Reference

| Input | Output | Sub-dispatches |
|---|---|---|
| Task list (in memory) + iteration context | Per-task result list | Implementer subagents (one per task, sequential) |

## Deferred to later plans

Spec-compliance reviewer dispatch, code-quality reviewer dispatch, parallel adversarial review (2 reviewers per stage), boxing-in check, re-dispatch loop on review failures, model selection rules.
