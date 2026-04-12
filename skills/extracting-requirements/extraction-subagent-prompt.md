# Extraction Subagent Prompt Template

Use this template when dispatching an extraction subagent. Fill in the bracketed values.

The spec taxonomy drives proof seam defaults:
- Source in `test-vectors/` → default seam `unit`
- Source in `contracts/` → default seam `integration`
- Source in `domains/` → default seam `integration` (upgrade to `app-level` if AC describes user-visible behavior)
- Source in `journeys/` → default seam `e2e`

## Standard Extraction (domains, contracts, test-vectors)

Dispatch a subagent with this prompt. Description: "Extract stories + scenarios from [source description]"

~~~
You are extracting testable requirements and behavior scenarios from spec documentation.

    ## Your Input

    The following spec content is from [source_file] (lines [start_line]-[end_line]):

    ---
    [chunk content pasted here]
    ---

    ## Your Job

    Read the spec content and produce TWO outputs: story cards and scenario cards.

    ### Output Format

    Produce this EXACT JSON structure:

    {
      "stories": [
        {
          "title": "Short imperative title",
          "epic_theme": "Domain grouping theme",
          "as_a": "actor role",
          "i_want": "capability",
          "so_that": "benefit",
          "acceptance_criteria": [
            {
              "id": "AC-1",
              "text": "Specific testable criterion with expected behavior",
              "behavioral_impact": "none|local|cross-surface|journey",
              "proof_seam": "unit|integration|app-level|process-level|e2e"
            }
          ],
          "sources": [
            {"file": "[source_file]", "lines": "[relevant line range]"}
          ]
        }
      ],
      "scenarios": [
        {
          "title": "Descriptive scenario title",
          "kind": "surface|failure-recovery|contract",
          "proof_seam": "unit|integration|app-level|process-level|e2e",
          "preconditions": ["precondition 1"],
          "steps": [
            {"action": "what happens", "expected": ["what must be true"]}
          ],
          "final_observables": ["what must be true after the scenario"],
          "owning_story_titles": ["title of story this scenario proves"],
          "sources": [
            {"file": "[source_file]", "lines": "[relevant line range]"}
          ]
        }
      ]
    }

    ### Story Rules

    - Every story MUST have at least one acceptance criterion
    - Each AC MUST include behavioral_impact and proof_seam
    - behavioral_impact: "none" = internal detail; "local" = one surface; "cross-surface" = multiple surfaces; "journey" = multi-step flow
    - proof_seam: the cheapest test level that can falsify the behavior. Defaults: [DEFAULT_SEAM based on source directory]
    - Sources must cite the specific file and line range
    - Do NOT assign STORY-NNNN or EPIC-NNN IDs — the aggregator does that
    - Do NOT attempt deduplication — the aggregator handles that
    - Do NOT invent requirements not present in the spec

    ### Scenario Rules

    - If ANY AC has behavioral_impact other than "none", there MUST be at least one scenario that covers it
    - Scenarios describe observable behavior, not implementation
    - Multiple ACs from different stories can share one scenario
    - One story may need multiple scenarios
    - For failure-recovery scenarios: preconditions include the failure state; action is the recovery; observables are the recovered state
    - proof_seam must match or exceed the highest proof_seam of the ACs it covers
    - owning_story_titles references story titles (not IDs, which don't exist yet)

    ### When to Emit Scenarios

    Emit a scenario when the spec describes behavior that is:
    - Observable by a user, operator, or external system
    - Verifiable by checking state, output, or side effects
    - Not purely internal implementation detail

    Do NOT emit scenarios for:
    - Internal data structures with no external effect
    - Implementation approach choices
    - Non-normative commentary

    Output ONLY the JSON object. No other text, no markdown fences, no explanation.
~~~

## Journey Extraction (journeys/)

For chunks from journey spec files, use this variant instead. Journey specs have a sequential step structure that must be preserved as a journey scenario chain.

Dispatch a subagent with this prompt. Description: "Extract stories + journey scenario from [source description]"

~~~
You are extracting testable requirements and a journey scenario chain
from a user journey spec.

    ## Your Input

    The following journey spec is from [source_file] (lines [start_line]-[end_line]):

    ---
    [chunk content pasted here]
    ---

    ## Your Job

    This is a USER JOURNEY — a sequential multi-step flow. Produce:
    1. Story cards for each implementable responsibility
    2. ONE journey scenario chain that preserves the complete step sequence

    ### Output Format

    {
      "stories": [
        {
          "title": "Short imperative title",
          "epic_theme": "Domain grouping theme",
          "as_a": "actor role",
          "i_want": "capability",
          "so_that": "benefit",
          "acceptance_criteria": [
            {
              "id": "AC-1",
              "text": "Specific testable criterion",
              "behavioral_impact": "local|cross-surface|journey",
              "proof_seam": "unit|integration|app-level|process-level|e2e"
            }
          ],
          "sources": [
            {"file": "[source_file]", "lines": "[relevant line range]"}
          ]
        }
      ],
      "scenarios": [
        {
          "title": "Journey title from spec",
          "kind": "journey",
          "proof_seam": "e2e",
          "preconditions": ["from the spec's Pre-conditions section"],
          "steps": [
            {
              "action": "User action or system event from step N",
              "expected": [
                "System response 1 from step N",
                "System response 2 from step N"
              ]
            }
          ],
          "final_observables": [
            "What must be true when the journey completes"
          ],
          "owning_story_titles": ["titles of stories this journey exercises"],
          "sources": [
            {"file": "[source_file]", "lines": "[relevant line range]"}
          ]
        }
      ]
    }

    ### Journey-Specific Rules

    - Preserve the COMPLETE step sequence from the spec — do not skip or summarize steps
    - Each step in the journey becomes one entry in "steps"
    - User actions and system responses from the same spec step go in one steps entry
    - The journey scenario's proof_seam is ALWAYS "e2e"
    - All story ACs that describe behavior within this journey should reference this journey scenario
    - A single journey may produce many stories (one per implementable subsystem touched)

    ### Story Rules (same as standard extraction)

    - Every AC MUST include behavioral_impact and proof_seam
    - Journey ACs that describe assembled behavior get proof_seam "e2e"
    - ACs for internal subsystem details within the journey can use lower seams
    - Sources must cite the specific file and line range
    - Do NOT assign IDs — the aggregator does that

    Output ONLY the JSON object. No other text, no markdown fences, no explanation.
~~~
