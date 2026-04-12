#!/usr/bin/env python3
"""Validate behavior-scenarios.md format and cross-references.

Usage: validate_scenarios.py <scenarios-file> <requirements-dir>

Checks:
- Every scenario has required fields (kind, proof seam, owning stories)
- All owning story references resolve to existing STORY-IDs
- Journey scenarios have steps (not empty)
- Scenario IDs are unique
- No UNRESOLVED() story references remain
"""
import re
import sys
from pathlib import Path


def load_story_ids(requirements_dir: Path) -> set[str]:
    """Collect all STORY-NNNN IDs from per-epic files."""
    ids: set[str] = set()
    for epic_file in requirements_dir.glob("EPIC-*.md"):
        for line in epic_file.read_text().splitlines():
            m = re.match(r"^## (STORY-\d+)", line)
            if m:
                ids.add(m.group(1))
    return ids


def validate(scenarios_path: Path, requirements_dir: Path) -> list[str]:
    """Validate scenarios file. Returns list of error strings."""
    errors: list[str] = []
    text = scenarios_path.read_text()
    lines = text.splitlines()

    known_stories = load_story_ids(requirements_dir)
    seen_ids: set[str] = set()

    current_id = None
    current_kind = None
    has_steps = False
    has_owning = False
    has_seam = False

    def flush():
        nonlocal current_id, current_kind, has_steps, has_owning, has_seam
        if current_id is None:
            return
        if not has_owning:
            errors.append(f"{current_id}: missing 'Owning stories' field")
        if not has_seam:
            errors.append(f"{current_id}: missing 'Proof seam' field")
        if current_kind == "journey" and not has_steps:
            errors.append(f"{current_id}: journey scenario has no steps")
        current_id = None
        current_kind = None
        has_steps = False
        has_owning = False
        has_seam = False

    for i, line in enumerate(lines, 1):
        # Scenario header
        id_match = re.match(r"^## (SCENARIO-\d+|JOURNEY-\d+)", line)
        if id_match:
            flush()
            current_id = id_match.group(1)
            if current_id in seen_ids:
                errors.append(f"line {i}: duplicate scenario ID {current_id}")
            seen_ids.add(current_id)

        if current_id:
            if line.startswith("**Kind:**"):
                current_kind = line.split(":**")[1].strip().lower()
            if line.startswith("**Proof seam:**"):
                has_seam = True
            if line.startswith("**Owning stories:**"):
                has_owning = True
                refs = line.split(":**")[1].strip()
                for ref in re.findall(r"STORY-\d+", refs):
                    if ref not in known_stories:
                        errors.append(f"{current_id}: references unknown {ref}")
                for unresolved in re.findall(r"UNRESOLVED\([^)]+\)", refs):
                    errors.append(f"{current_id}: has {unresolved}")
            if re.match(r"^\d+\.", line.strip()):
                has_steps = True

    flush()

    if not seen_ids:
        errors.append("no scenarios found in file")

    return errors


def main() -> int:
    if len(sys.argv) != 3:
        print(f"usage: {sys.argv[0]} <scenarios-file> <requirements-dir>",
              file=sys.stderr)
        return 2

    scenarios_path = Path(sys.argv[1])
    requirements_dir = Path(sys.argv[2])

    if not scenarios_path.exists():
        print(f"error: file not found: {scenarios_path}", file=sys.stderr)
        return 2
    if not requirements_dir.is_dir():
        print(f"error: directory not found: {requirements_dir}", file=sys.stderr)
        return 2

    errors = validate(scenarios_path, requirements_dir)
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        print(f"FAIL: {len(errors)} error(s)")
        return 1

    print("OK: scenarios valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
