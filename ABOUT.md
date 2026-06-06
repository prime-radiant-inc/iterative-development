# iterative-development

> A Claude Code plugin that drives an autonomous, audited implementation loop for projects with large, comprehensive, or ambiguous specs; pairs with Superpowers.

**Family:** superpowers · **Type:** tool · **Lifecycle:** production · **Owner:** obra

## What it does
The top-level iterative-development skill orchestrates a full lifecycle: extract requirements with proof obligations from spec collateral, scope a walking skeleton plus ordered roadmap, run audited sprints (sentinel baseline, scope review, code+evidence tasks, impacted/sentinel scenario runs), and run PAR-based auditors across a three-tier review. Completion means passing behavior evidence for every externally observable requirement, not just finished stories. It ships six skills plus Python validation scripts.

## How it fits
- Depends on: — (Conceptually pairs with Superpowers skills — brainstorming, TDD, PAR, verification — and bundles a ported copy of the PAR methodology under skills/shared/; these are skill cross-references, not code/runtime imports of another repo.)
- Used by: [iterative-development-example-ghost-pepper](https://github.com/prime-radiant-inc/iterative-development-example-ghost-pepper) was built using this methodology.
- External: Claude Code (runs as a plugin and dispatches Claude subagents); distributed via prime-radiant-marketplace.

## Runtime & data
- Runs: Installed as a Claude Code plugin; not a long-running service.
- Data in: Spec collateral, requirements.
- Data out: Extracted requirements, roadmap, behavior-evidence corpus, implemented code.

<!-- Maintained by the maintaining-project-map skill. Do not hand-edit; regenerated. -->
