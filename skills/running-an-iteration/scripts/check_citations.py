#!/usr/bin/env python3
"""Verify every story cited in a roadmap exists in the requirements directory.

Usage: check_citations.py <roadmap.md> <requirements-dir>

The requirements directory contains per-epic files (EPIC-NNN.md), each
with ## STORY-NNNN headers.

Exit code: 0 if all citations valid, 1 if any missing, 2 on usage error.
"""
import re
import sys
from pathlib import Path


def extract_cited_stories(roadmap_content: str) -> set[str]:
    """Extract all STORY-NNNN references from roadmap content."""
    return set(re.findall(r"STORY-\d+", roadmap_content))


def extract_defined_stories(req_path: Path) -> set[str]:
    """Extract all ## STORY-NNNN headers from requirements path.

    Accepts either a directory of per-epic .md files or a single .md file
    (for backward compatibility with test fixtures).
    """
    defined: set[str] = set()
    if req_path.is_dir():
        for md_file in sorted(req_path.glob("*.md")):
            defined.update(re.findall(r"^## (STORY-\d+)", md_file.read_text(), re.MULTILINE))
    else:
        defined.update(re.findall(r"^## (STORY-\d+)", req_path.read_text(), re.MULTILINE))
    return defined


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: check_citations.py <roadmap.md> <requirements-dir-or-file>",
              file=sys.stderr)
        return 2

    roadmap_path = Path(sys.argv[1])
    req_path = Path(sys.argv[2])

    if not roadmap_path.exists():
        print(f"error: file not found: {roadmap_path}", file=sys.stderr)
        return 2
    if not req_path.exists():
        print(f"error: not found: {req_path}", file=sys.stderr)
        return 2

    cited = extract_cited_stories(roadmap_path.read_text())
    defined = extract_defined_stories(req_path)

    missing = cited - defined
    if missing:
        for story_id in sorted(missing):
            print(f"error: {story_id} cited in roadmap but not found in requirements",
                  file=sys.stderr)
        return 1

    print(f"OK: all {len(cited)} cited stories exist in requirements")
    return 0


if __name__ == "__main__":
    sys.exit(main())
