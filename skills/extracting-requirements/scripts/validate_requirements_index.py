#!/usr/bin/env python3
"""Validate a requirements-index.md file.

Usage: validate_requirements_index.py <file>

Checks:
- Contains at least one STORY-NNNN header with valid ID
- Detects malformed STORY- headers (missing digits)
- Each story has: Epic, Title, acceptance criteria, sources, status

Exit code: 0 on success, 1 on validation failure, 2 on invocation error.
"""
import re
import sys
from pathlib import Path


def validate_requirements_index(content: str) -> list[str]:
    """Validate a requirements-index.md file."""
    errors: list[str] = []

    story_pattern = re.compile(r"^## STORY-(\d+)\s*$", re.MULTILINE)
    bad_story_pattern = re.compile(r"^## STORY-\s*$", re.MULTILINE)

    if bad_story_pattern.search(content):
        errors.append("found malformed story id: STORY- header is missing digits")

    stories = story_pattern.findall(content)
    if not stories:
        errors.append("no valid STORY-NNNN headers found")
        return errors

    for match in story_pattern.finditer(content):
        story_id = f"STORY-{match.group(1)}"
        start = match.end()
        next_h2 = re.search(r"^## ", content[start:], re.MULTILINE)
        end = start + next_h2.start() if next_h2 else len(content)
        section = content[start:end]

        for required in ("**Epic:**", "**Title:**", "**Acceptance criteria:**",
                         "**Sources:**", "**Status:**"):
            if required not in section:
                errors.append(f"{story_id}: missing required field {required}")

    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_requirements_index.py <file>", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 2

    errors = validate_requirements_index(path.read_text())
    if errors:
        for err in errors:
            print(f"error: {err}", file=sys.stderr)
        return 1

    print(f"OK: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
