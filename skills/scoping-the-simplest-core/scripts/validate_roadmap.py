#!/usr/bin/env python3
"""Validate a roadmap.md file.

Usage: validate_roadmap.py <file>

Checks:
- Contains a "Walking skeleton (ITER-0000)" section
- Walking skeleton section has Intent, Status, Stories committed, Journey scenario
- Contains an "Iteration list" section

Exit code: 0 on success, 1 on validation failure, 2 on invocation error.
"""
import sys
from pathlib import Path


def validate_roadmap(content: str) -> list[str]:
    """Validate a roadmap.md file."""
    errors: list[str] = []

    if "## Walking skeleton (ITER-0000)" not in content:
        errors.append("missing walking skeleton section (expected '## Walking skeleton (ITER-0000)')")

    if "## Iteration list" not in content:
        errors.append("missing iteration list section (expected '## Iteration list')")

    if "## Walking skeleton (ITER-0000)" in content:
        ws_start = content.index("## Walking skeleton (ITER-0000)")
        next_h2 = content.find("\n## ", ws_start + 1)
        ws_end = next_h2 if next_h2 != -1 else len(content)
        ws_section = content[ws_start:ws_end]
        for required in ("**Intent:**", "**Status:**", "**Stories committed:**", "**Journey scenario:**"):
            if required not in ws_section:
                errors.append(f"walking skeleton: missing required field {required}")

    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_roadmap.py <file>", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 2

    errors = validate_roadmap(path.read_text())
    if errors:
        for err in errors:
            print(f"error: {err}", file=sys.stderr)
        return 1

    print(f"OK: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
