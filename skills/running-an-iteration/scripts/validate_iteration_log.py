#!/usr/bin/env python3
"""Validate an iteration-log.md file.

Usage: validate_iteration_log.py <file>

Checks:
- Contains at least one ITER-NNNN section
- Each iteration section has Completed, Stories delivered, Tasks executed, Summary, Scenarios

Exit code: 0 on success, 1 on validation failure, 2 on invocation error.
"""
import re
import sys
from pathlib import Path


def validate_iteration_log(content: str) -> list[str]:
    """Validate an iteration-log.md file."""
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
                         "**Tasks executed:**", "**Scenarios:**", "**Summary:**"):
            if required not in section:
                errors.append(f"{iter_id}: missing required field {required}")

    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_iteration_log.py <file>", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 2

    errors = validate_iteration_log(path.read_text())
    if errors:
        for err in errors:
            print(f"error: {err}", file=sys.stderr)
        return 1

    print(f"OK: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
