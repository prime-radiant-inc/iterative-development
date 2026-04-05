#!/usr/bin/env python3
"""Validate iterative-development artifact files.

Usage: validate_artifact.py --type <type> <file>

Types: requirements-index, roadmap, iteration-log
Exit code: 0 on success, 1 on validation failure, 2 on invocation error.
"""
import argparse
import sys
from pathlib import Path


KNOWN_TYPES = ("requirements-index", "roadmap", "iteration-log")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate iterative-development artifacts")
    parser.add_argument("--type", required=True, help=f"Artifact type: one of {KNOWN_TYPES}")
    parser.add_argument("file", help="Path to artifact file")
    args = parser.parse_args()

    if args.type not in KNOWN_TYPES:
        print(f"error: unknown artifact type: {args.type}", file=sys.stderr)
        return 2

    path = Path(args.file)
    if not path.exists():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 2

    content = path.read_text()

    # Dispatch to type-specific validator (added in Tasks 3-5).
    validators = {
        "requirements-index": validate_requirements_index,
        "roadmap": validate_roadmap,
        "iteration-log": validate_iteration_log,
    }
    errors = validators[args.type](content)

    if errors:
        for err in errors:
            print(f"error: {err}", file=sys.stderr)
        return 1

    print(f"OK: {path}")
    return 0


def validate_requirements_index(content: str) -> list[str]:
    """Validate a requirements-index.md file.

    Checks:
    - Contains at least one STORY-NNNN header with valid ID
    - Each story has: Epic, Title, acceptance criteria, sources, status
    - Each epic referenced by a story exists as an EPIC-NNN header
    """
    import re

    errors: list[str] = []

    story_pattern = re.compile(r"^## STORY-(\d+)\s*$", re.MULTILINE)
    bad_story_pattern = re.compile(r"^## STORY-\s*$", re.MULTILINE)
    epic_pattern = re.compile(r"^## EPIC-(\d+)\s*", re.MULTILINE)

    # Catch malformed STORY-/EPIC- IDs (missing digits)
    if bad_story_pattern.search(content):
        errors.append("found malformed story id: STORY- header is missing digits")

    stories = story_pattern.findall(content)
    if not stories:
        errors.append("no valid STORY-NNNN headers found")
        return errors

    # Per-story required sections
    for match in story_pattern.finditer(content):
        story_id = f"STORY-{match.group(1)}"
        # Find the section bounds (until next ## or end)
        start = match.end()
        next_h2 = re.search(r"^## ", content[start:], re.MULTILINE)
        end = start + next_h2.start() if next_h2 else len(content)
        section = content[start:end]

        for required in ("**Epic:**", "**Title:**", "**Acceptance criteria:**",
                         "**Sources:**", "**Status:**"):
            if required not in section:
                errors.append(f"{story_id}: missing required field {required}")

    return errors


def validate_roadmap(content: str) -> list[str]:
    """Return list of error messages. Empty list means valid. Expanded in Task 4."""
    return ["roadmap validator not yet implemented"]


def validate_iteration_log(content: str) -> list[str]:
    """Return list of error messages. Empty list means valid. Expanded in Task 5."""
    return ["iteration-log validator not yet implemented"]


if __name__ == "__main__":
    sys.exit(main())
