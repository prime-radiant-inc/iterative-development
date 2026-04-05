#!/usr/bin/env python3
"""Validate a SKILL.md file.

Usage: validate_skill.py <path/to/SKILL.md>

Checks:
- File exists and is readable
- Starts with YAML frontmatter (--- delimited)
- Frontmatter contains 'name' and 'description' fields
- 'name' field uses only letters, numbers, hyphens
- 'description' field starts with "Use when"
- Body word count is under 500 words (warning if over — not an error)
"""
import re
import sys
from pathlib import Path


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Parse a simple YAML-like frontmatter (key: value lines between --- delimiters).

    Returns (frontmatter_dict, body). Returns ({}, content) if no frontmatter.
    """
    if not content.startswith("---\n"):
        return {}, content

    end_marker = content.find("\n---\n", 4)
    if end_marker == -1:
        return {}, content

    fm_text = content[4:end_marker]
    body = content[end_marker + 5:]

    fm: dict = {}
    current_key: str | None = None
    for line in fm_text.splitlines():
        if not line.strip():
            continue
        if line.startswith(" ") and current_key:
            fm[current_key] = fm[current_key] + " " + line.strip()
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip()
            fm[key] = value
            current_key = key
    return fm, body


def validate(path: Path) -> tuple[list[str], list[str]]:
    """Return (errors, warnings). Errors cause validation failure; warnings do not."""
    errors: list[str] = []
    warnings: list[str] = []
    content = path.read_text()

    fm, body = parse_frontmatter(content)

    if not fm:
        errors.append("missing or malformed YAML frontmatter (expected --- delimited block at start of file)")
        return errors, warnings

    if "name" not in fm:
        errors.append("frontmatter missing required 'name' field")
    else:
        name = fm["name"]
        if not re.fullmatch(r"[a-zA-Z0-9-]+", name):
            errors.append(f"frontmatter 'name' has invalid characters (must be letters/digits/hyphens): {name}")

    if "description" not in fm:
        errors.append("frontmatter missing required 'description' field")
    else:
        desc = fm["description"]
        if not desc.lower().startswith("use when"):
            errors.append(f"frontmatter 'description' should start with 'Use when' but starts with: {desc[:30]!r}")

    # Word count is a target per writing-skills guidance, not a hard limit.
    word_count = len(body.split())
    if word_count > 500:
        warnings.append(f"body word count {word_count} exceeds 500 (target per writing-skills guidance)")

    return errors, warnings


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_skill.py <path/to/SKILL.md>", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 2

    errors, warnings = validate(path)
    for warn in warnings:
        print(f"warning: {warn}", file=sys.stderr)
    if errors:
        for err in errors:
            print(f"error: {err}", file=sys.stderr)
        return 1

    print(f"OK: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
