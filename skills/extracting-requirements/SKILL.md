---
name: extracting-requirements
description: Use when starting an iterative-development run on human spec collateral — reads the spec, produces a structured requirements-index.md containing story cards and epics with stable IDs.
---

# Extracting Requirements

## Overview

Reads arbitrary human spec collateral (one file, a directory, or a large prose dump) and produces `docs/superpowers/iterations/requirements-index.md` — the plugin's internal backlog of story cards and epics with stable global IDs.

**This is Plan 1 — walking skeleton implementation. Parallel extraction, chunking, map-reduce aggregation, hierarchical reduce, and huge-spec decomposition are NOT yet implemented and will be added in Plan 2.**

## When to Use

Invoked by `iterative-development` during bootstrap, or standalone when you need to regenerate the requirements index from human spec collateral.

## Walking Skeleton Behavior (Plan 1)

Read the full spec in a single subagent pass — no chunking, no parallel dispatch.

1. Receive the spec path as input (a file or directory).
2. Dispatch a single extraction subagent with the complete spec contents.
3. The subagent produces story cards following the format in `tests/fixtures/requirements-index.example.md`:
   - Each story has a `STORY-NNNN` ID (assigned sequentially starting from 0001)
   - Each story has an Epic reference, Title, As-a/I-want/So-that, Acceptance criteria, Sources, Status
   - Each unique epic theme gets an `EPIC-NNN` ID
4. Write the result to `docs/superpowers/iterations/requirements-index.md`.
5. Run `scripts/validate_artifact.py --type requirements-index <path>` to verify the output is well-formed.
6. If validation fails, fix the formatting issues and re-validate.

**Limits for Plan 1:** the spec must fit in a single subagent's context (approximately 100K tokens). Large specs will be supported in Plan 2.

## Quick Reference

| Input | Output | Validator |
|---|---|---|
| Spec file/directory | `docs/superpowers/iterations/requirements-index.md` | `scripts/validate_artifact.py --type requirements-index` |

## Deferred to later plans

Chunking by file/section, parallel extraction subagents, map-reduce aggregation, hierarchical reduce for very large specs, decomposition for huge specs (>1M tokens), incremental re-extraction when spec files change mid-project.
