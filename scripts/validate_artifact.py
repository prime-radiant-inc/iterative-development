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
    - Detects malformed STORY- headers (missing digits)
    - Each story has: Epic, Title, acceptance criteria, sources, status
    """
    import re

    errors: list[str] = []

    story_pattern = re.compile(r"^## STORY-(\d+)\s*$", re.MULTILINE)
    bad_story_pattern = re.compile(r"^## STORY-\s*$", re.MULTILINE)

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
    """Validate a roadmap.md file.

    Checks:
    - Contains a "Walking skeleton (ITER-0000)" section
    - Walking skeleton section has Intent, Status, Stories committed
    - Contains an "Iteration list" section
    """
    errors: list[str] = []

    if "## Walking skeleton (ITER-0000)" not in content:
        errors.append("missing walking skeleton section (expected '## Walking skeleton (ITER-0000)')")

    if "## Iteration list" not in content:
        errors.append("missing iteration list section (expected '## Iteration list')")

    # Walking skeleton required fields
    if "## Walking skeleton (ITER-0000)" in content:
        ws_start = content.index("## Walking skeleton (ITER-0000)")
        next_h2 = content.find("\n## ", ws_start + 1)
        ws_end = next_h2 if next_h2 != -1 else len(content)
        ws_section = content[ws_start:ws_end]
        for required in ("**Intent:**", "**Status:**", "**Stories committed:**"):
            if required not in ws_section:
                errors.append(f"walking skeleton: missing required field {required}")

    return errors


def validate_iteration_log(content: str) -> list[str]:
    """Validate an iteration-log.md file.

    Checks:
    - Contains at least one ITER-NNNN section
    - Each iteration section has Completed, Stories delivered, Tasks executed, Summary
    """
    import re

    errors: list[str] = []

    iter_pattern = re.compile(r"^## ITER-(\d+)", re.MULTILINE)
    iters = list(iter_pattern.finditer(content))

    if not iters:
        errors.append("no iteration sections found (expected at least one '## ITER-NNNN')")
        return errors

    for idx, match in enumerate(iters):
        iter_id = f"ITER-{match.group(1)}"
        start = match.end()
        end = iters[idx + 1].start() if idx + 1 < len(iters) else len(content)
        section = content[start:end]

        for required in ("**Completed:**", "**Stories delivered:**",
                         "**Tasks executed:**", "**Summary:**"):
            if required not in section:
                errors.append(f"{iter_id}: missing required field {required}")

    return errors


if __name__ == "__main__":
    sys.exit(main())
