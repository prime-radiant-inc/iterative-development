# iterative-development

A Claude Code plugin that drives an autonomous, audited implementation loop for projects with large, comprehensive, or ambiguous specs. Pairs with [superpowers](https://github.com/obra/superpowers).

## When to use it

Use this plugin when:

- Your spec is large, comprehensive, or ambiguous (10+ files, 100+ requirements).
- You want the product in a working, testable state at every iteration boundary.
- You want an autonomous audited loop rather than a single upfront plan.
- The `superpowers:writing-plans` → `superpowers:subagent-driven-development` flow has lost the plot on this project before.

Do **not** use it for small, bounded projects — `superpowers:writing-plans` is simpler and more appropriate.

## What it does

The top-level `iterative-development` skill orchestrates the full lifecycle:

1. **Extract requirements** — chunks the spec, dispatches parallel extraction subagents, and produces stories with proof obligations plus behavior scenarios. Aggregates into per-epic files, a behavior-scenarios corpus, and a coverage ledger.
2. **Scope the simplest core** — defines the walking skeleton iteration (ITER-0000) and an ordered roadmap of follow-on iterations. The walking skeleton must close at least one real journey scenario, not just compile.
3. **Run iterations** — sentinel baseline → scope review → decompose code + evidence tasks → implement → impacted + sentinel scenario runs → wrap up.
4. **Audit progress** — paired auditors run a three-tier review (deep evidence, impacted behavior, sentinel corpus) using parallel adversarial review (PAR). Gaps feed back into the backlog.
5. **Terminate** — when the roadmap is drained and a final behavior-evidence audit passes, the loop exits.

Completion means the product has passing behavior evidence at the correct seam for every externally observable requirement — not just that stories are marked done.

## Skills

| Skill | Role |
|---|---|
| `iterative-development` | Top-level orchestrator for the autonomous loop. |
| `extracting-requirements` | Chunk + parallel-extract + aggregate stories and scenarios from spec collateral. |
| `scoping-the-simplest-core` | Define walking skeleton and roadmap. |
| `running-an-iteration` | Execute one sprint end-to-end. |
| `implementing-tasks` | Per-task implementer with evidence discipline. |
| `auditing-progress` | PAR-based audits at iteration and corpus level. |

## Installation

Install from the Prime Radiant marketplace:

```
/plugin marketplace add prime-radiant-inc/prime-radiant-marketplace
/plugin install iterative-development@prime-radiant-marketplace
```

Restart Claude Code after installing.

## Running the tests

```
./scripts/run_validation_suite.sh
```

Individual test files can be run with `pytest tests/`.

## Relationship to superpowers

This plugin depends conceptually on skills from the `superpowers` plugin (brainstorming, TDD, parallel adversarial review, verification-before-completion). Install `superpowers` alongside `iterative-development` for the intended experience.

## License

Apache License 2.0. See [LICENSE](LICENSE).
