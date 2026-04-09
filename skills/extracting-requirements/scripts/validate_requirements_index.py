#!/usr/bin/env python3
"""Validate requirements files (per-epic or single index).

Usage: validate_requirements_index.py <path>

If <path> is a directory, validates all .md files in it as per-epic files.
If <path> is a file, validates it as a single requirements-index.md.

Checks per file:
- Contains at least one STORY-NNNN header with valid ID
- Detects malformed STORY- headers (missing digits)
- Each story has: Epic, Title, acceptance criteria, sources, status

Exit code: 0 on success, 1 on validation failure, 2 on invocation error.
"""
import re
import sys
from pathlib import Path


def validate_content(content: str, source_name: str) -> list[str]:
    """Validate requirements content from a single file."""
    errors: list[str] = []

    story_pattern = re.compile(r"^## STORY-(\d+)\s*$", re.MULTILINE)
    bad_story_pattern = re.compile(r"^## STORY-\s*$", re.MULTILINE)

    if bad_story_pattern.search(content):
        errors.append(f"{source_name}: found malformed story id: STORY- header is missing digits")

    stories = story_pattern.findall(content)
    if not stories:
        errors.append(f"{source_name}: no valid STORY-NNNN headers found")
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
                errors.append(f"{source_name}: {story_id}: missing required field {required}")

    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_requirements_index.py <path>", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"error: not found: {path}", file=sys.stderr)
        return 2

    all_errors: list[str] = []

    if path.is_dir():
        md_files = sorted(path.glob("*.md"))
        if not md_files:
            print(f"error: no .md files found in {path}", file=sys.stderr)
            return 1
        for md_file in md_files:
            all_errors.extend(validate_content(md_file.read_text(), md_file.name))
    else:
        all_errors.extend(validate_content(path.read_text(), path.name))

    if all_errors:
        for err in all_errors:
            print(f"error: {err}", file=sys.stderr)
        return 1

    print(f"OK: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
