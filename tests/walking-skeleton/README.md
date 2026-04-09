# Walking Skeleton Dogfood Procedure

This directory contains the end-to-end manual verification for Plan 1 of the iterative-development plugin. Because the plugin is instructional (skills are executed by Claude in-session), there is no fully-automated end-to-end test. This procedure is the verification.

## Prerequisites

- The plugin is installed (or available as a local plugin marketplace entry)
- Python 3 is available
- A clean directory to run the dogfood in (do NOT run in the plugin's own repo)
- All unit tests pass: `python3 -m unittest discover tests/`
- All skill files validate: `bash scripts/run_validation_suite.sh`

## Procedure

### 1. Set up a clean dogfood workspace

```bash
mkdir /tmp/walking-skeleton-dogfood
cd /tmp/walking-skeleton-dogfood
cp <plugin-repo>/tests/walking-skeleton/input-spec/spec.md .
git init && git add spec.md && git commit -m "initial: sample spec"
```

### 2. Invoke the plugin

In a Claude Code session running in `/tmp/walking-skeleton-dogfood`, ask Claude to use the `iterative-development` skill on `spec.md`.

Expected high-level flow:
1. Claude invokes `iterative-development` (orchestrator)
2. Orchestrator invokes `extracting-requirements` → creates per-epic files in `docs/superpowers/iterations/requirements/`
3. Orchestrator invokes `scoping-the-simplest-core` → creates `docs/superpowers/iterations/roadmap.md`
4. Orchestrator enters the iteration loop:
   - Invokes `running-an-iteration` → picks ITER-0000, decomposes into tasks
   - `running-an-iteration` dispatches `implementing-tasks` → writes TDD-style code that implements greet
   - `running-an-iteration` updates epic files in `requirements/`, `roadmap.md`, appends to `iteration-log.md`
   - Orchestrator invokes `auditing-progress` → confirms ACs pass
   - Roadmap is empty + audit clean → orchestrator terminates

### 3. Verify artifacts

Check that the following files exist and validate:

```bash
python3 <plugin-repo>/skills/extracting-requirements/scripts/validate_requirements_index.py docs/superpowers/iterations/requirements/
python3 <plugin-repo>/skills/scoping-the-simplest-core/scripts/validate_roadmap.py docs/superpowers/iterations/roadmap.md
python3 <plugin-repo>/skills/running-an-iteration/scripts/validate_iteration_log.py docs/superpowers/iterations/iteration-log.md
```

Expected: all three print `OK: <path>`.

### 4. Verify the final product works

Whatever executable the plugin produced (e.g., `greet.py`, `greet.sh`, or a compiled binary), verify it matches the spec:

```bash
./greet Alice
# Expected output: Hello, Alice!
# Expected exit code: 0

./greet 2>&1
# Expected output: usage: greet <name>
# Expected exit code: non-zero
```

### 5. Verify the git history

The implementation should be committed in small TDD-sized commits:

```bash
git log --oneline
# Expected: multiple commits, at minimum:
# - failing test for greeting
# - implementation of greeting
# - failing test for error case
# - implementation of error handling
```

## Acceptance criteria for Plan 1 walking skeleton

The walking skeleton passes if:

- [ ] All six skills are invoked in the correct order
- [ ] All three artifacts are created in `docs/superpowers/iterations/`
- [ ] All three artifacts validate against their format validators
- [ ] The final product satisfies both functional requirements (F-1 and F-2) from `spec.md`
- [ ] The git history shows TDD-style commits (test → implementation)
- [ ] The orchestrator terminates cleanly (does not run indefinitely or crash)

If any of these fail, the walking skeleton is not complete and Plan 1 is not done.

## Known limitations (deferred to later plans)

This is the walking skeleton. It does NOT:
- Parallel-dispatch anything
- Run parallel adversarial review
- Audit previously-done work (only the just-finished iteration)
- Chunk or map-reduce the spec (reads it in one pass)
- Handle huge specs (>100K tokens in the spec)
- Handle human interrupts between iterations
- Recover from crashes mid-iteration

These capabilities are added in Plans 2-7.
