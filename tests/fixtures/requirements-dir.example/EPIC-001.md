# EPIC-001 — Greeting commands

**Summary:** Commands that greet the user with a personalized message.
**Stories:** STORY-0001
**Primary sources:** `spec.md:1-20`
**Status:** 0/1 done

## STORY-0001

**Epic:** EPIC-001 — Greeting commands
**Title:** User gets a personalized greeting

**As a** command-line user
**I want** to invoke a greet command with my name
**So that** I see a personalized greeting message

**Acceptance criteria:**
- AC-1: Running `greet <name>` prints `Hello, <name>!` to stdout
- AC-2: Running `greet` with no argument prints a usage message to stderr and exits non-zero

**Sources:**
- `spec.md:1-20`

**Status:** pending
