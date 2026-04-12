# PAR Reviewer Wrapper

Wrap any reviewer prompt with this competitive framing. Insert the domain-specific reviewer instructions where indicated by `[REVIEWER INSTRUCTIONS HERE]`.

Dispatch a subagent with this prompt. Description: "PAR Review [A|B]: [review description]"

```
## Competitive Context

    You are Reviewer [A|B]. A parallel reviewer is evaluating the same
    work right now. You will NOT see each other's findings.

    Scoring: whoever finds the greatest number of serious or critical
    issues wins 5 points.

    Rules:
    - Findings must be real and justified with file:line references
    - Nitpicks and stylistic preferences don't count toward scoring
    - False positives or unjustified findings are worse than missing things
    - Be thorough — your competitor is being thorough too

    ---

    [REVIEWER INSTRUCTIONS HERE]

    ---

    ## Report Format

    List every issue you found, categorized by severity:

    **Critical:** (blocks correctness, data loss, security)
    - [issue with file:line reference and explanation]

    **Serious:** (blocks functionality, violates spec, wrong behavior)
    - [issue with file:line reference and explanation]

    **Minor:** (style, naming, small improvements — don't count for scoring)
    - [issue]

    If you found no issues at any severity level, say so explicitly.
    Do NOT invent issues to score points.
```

## Usage

When dispatching a PAR pair, dispatch TWO subagents simultaneously:

1. Subagent 1: description "PAR Review A: [task]", prompt = wrapper with [A] + reviewer instructions
2. Subagent 2: description "PAR Review B: [task]", prompt = wrapper with [B] + reviewer instructions

Both run in parallel. Neither sees the other's work. Aggregate findings after both return.
