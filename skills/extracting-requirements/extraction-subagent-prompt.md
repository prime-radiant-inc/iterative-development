# Extraction Subagent Prompt Template

Use this template when dispatching an extraction subagent. Fill in the bracketed values.

```
Agent tool (general-purpose):
  description: "Extract stories from [source description]"
  prompt: |
    You are extracting testable requirements from spec documentation.

    ## Your Input

    The following spec content is from [source_file] (lines [start_line]-[end_line]):

    ---
    [chunk content pasted here]
    ---

    ## Your Job

    Read the spec content above and extract every testable requirement as a
    story card. For each distinct requirement you find, produce a story in
    this EXACT JSON format:

    {
      "stories": [
        {
          "title": "Short imperative title (e.g., 'User creates a new task')",
          "epic_theme": "Domain grouping theme (e.g., 'Task Management')",
          "as_a": "actor role (e.g., 'command-line user')",
          "i_want": "capability (e.g., 'to run task add <title>')",
          "so_that": "benefit (e.g., 'a new task is created and tracked')",
          "acceptance_criteria": [
            "AC-1: Specific testable criterion with expected behavior",
            "AC-2: Another testable criterion"
          ],
          "sources": [
            {"file": "[source_file]", "lines": "[relevant line range]"}
          ]
        }
      ]
    }

    ## Rules

    - Every story MUST have at least one acceptance criterion that is directly testable
    - Acceptance criteria must describe observable behavior (input → expected output)
    - Sources must cite the specific file and line range where the requirement appears
    - Propose an epic_theme for grouping related stories — use a short domain name
    - Do NOT assign STORY-NNNN or EPIC-NNN IDs — the aggregator does that
    - Do NOT attempt deduplication — the aggregator handles that
    - Do NOT invent requirements not present in the spec content
    - If the spec is ambiguous, extract what is clearly stated and note the ambiguity
    - Output ONLY the JSON object. No other text, no markdown fences, no explanation.
```
