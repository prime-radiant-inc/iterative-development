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
    """Return list of error messages. Empty list means valid. Expanded in Task 3."""
    return ["requirements-index validator not yet implemented"]


def validate_roadmap(content: str) -> list[str]:
    """Return list of error messages. Empty list means valid. Expanded in Task 4."""
    return ["roadmap validator not yet implemented"]


def validate_iteration_log(content: str) -> list[str]:
    """Return list of error messages. Empty list means valid. Expanded in Task 5."""
    return ["iteration-log validator not yet implemented"]


if __name__ == "__main__":
    sys.exit(main())
