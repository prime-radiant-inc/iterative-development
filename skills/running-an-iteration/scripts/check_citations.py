#!/usr/bin/env python3
"""Verify every story cited in a roadmap exists in the requirements index.

Usage: check_citations.py <roadmap.md> <requirements-index.md>

Exit code: 0 if all citations valid, 1 if any missing, 2 on usage error.
"""
import re
import sys
from pathlib import Path


def extract_cited_stories(roadmap_content: str) -> set[str]:
    """Extract all STORY-NNNN references from roadmap content."""
    return set(re.findall(r"STORY-\d+", roadmap_content))


def extract_defined_stories(index_content: str) -> set[str]:
    """Extract all ## STORY-NNNN headers from requirements index."""
    return set(re.findall(r"^## (STORY-\d+)", index_content, re.MULTILINE))


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: check_citations.py <roadmap.md> <requirements-index.md>",
              file=sys.stderr)
        return 2

    roadmap_path = Path(sys.argv[1])
    index_path = Path(sys.argv[2])

    for p in (roadmap_path, index_path):
        if not p.exists():
            print(f"error: file not found: {p}", file=sys.stderr)
            return 2

    cited = extract_cited_stories(roadmap_path.read_text())
    defined = extract_defined_stories(index_path.read_text())

    missing = cited - defined
    if missing:
        for story_id in sorted(missing):
            print(f"error: {story_id} cited in roadmap but not found in requirements index",
                  file=sys.stderr)
        return 1

    print(f"OK: all {len(cited)} cited stories exist in requirements index")
    return 0


if __name__ == "__main__":
    sys.exit(main())
