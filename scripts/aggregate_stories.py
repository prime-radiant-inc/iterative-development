#!/usr/bin/env python3
"""Aggregate extracted story card JSONs into a requirements-index.md.

Usage: aggregate_stories.py <json-file>...

Takes one or more JSON files (each a list of story objects or {"stories": [...]}),
deduplicates by title, groups into epics by epic_theme, assigns stable IDs
(STORY-NNNN, EPIC-NNN), and outputs requirements-index.md to stdout.
"""
import json
import sys
from collections import OrderedDict
from pathlib import Path


def load_stories(paths: list[Path]) -> list[dict]:
    """Load and combine stories from multiple JSON files."""
    all_stories: list[dict] = []
    for p in paths:
        data = json.loads(p.read_text())
        if isinstance(data, list):
            all_stories.extend(data)
        elif isinstance(data, dict) and "stories" in data:
            all_stories.extend(data["stories"])
        else:
            print(f"warning: {p} has unexpected format, skipping", file=sys.stderr)
    return all_stories


def dedup_stories(stories: list[dict]) -> list[dict]:
    """Deduplicate stories by exact title match. Merges sources from duplicates."""
    seen: dict[str, dict] = OrderedDict()
    for story in stories:
        title = story.get("title", "").strip()
        if title in seen:
            existing_sources = seen[title].get("sources", [])
            for src in story.get("sources", []):
                if src not in existing_sources:
                    existing_sources.append(src)
            seen[title]["sources"] = existing_sources
        else:
            seen[title] = dict(story)  # copy to avoid mutating input
    return list(seen.values())


def group_into_epics(stories: list[dict]) -> dict[str, list[dict]]:
    """Group stories by epic_theme. Returns ordered dict {theme: [stories]}."""
    epics: dict[str, list[dict]] = OrderedDict()
    for story in stories:
        theme = story.get("epic_theme", "Uncategorized").strip()
        if theme not in epics:
            epics[theme] = []
        epics[theme].append(story)
    return epics


def format_requirements_index(epics: dict[str, list[dict]]) -> str:
    """Format epics and stories as requirements-index.md content."""
    lines: list[str] = ["# Requirements Index", ""]

    story_counter = 1
    epic_counter = 1

    # First pass: assign IDs and write epic headers
    for theme, stories in epics.items():
        epic_id = f"EPIC-{epic_counter:03d}"
        epic_counter += 1

        story_ids: list[str] = []
        for story in stories:
            sid = f"STORY-{story_counter:04d}"
            story["_id"] = sid
            story["_epic_id"] = epic_id
            story["_epic_theme"] = theme
            story_ids.append(sid)
            story_counter += 1

        primary_sources: set[str] = set()
        for s in stories:
            for src in s.get("sources", []):
                if isinstance(src, dict):
                    primary_sources.add(src.get("file", ""))
                elif isinstance(src, str):
                    primary_sources.add(src)

        lines.append(f"## {epic_id} — {theme}")
        lines.append("")
        lines.append(f"**Summary:** {theme}")
        lines.append(f"**Stories:** {', '.join(story_ids)}")
        if primary_sources:
            sources_str = ", ".join(f"`{s}`" for s in sorted(primary_sources) if s)
            lines.append(f"**Primary sources:** {sources_str}")
        lines.append(f"**Status:** 0/{len(stories)} done")
        lines.append("")

    # Second pass: write story cards
    for theme, stories in epics.items():
        for story in stories:
            sid = story["_id"]
            epic_id = story["_epic_id"]
            epic_theme = story["_epic_theme"]

            lines.append(f"## {sid}")
            lines.append("")
            lines.append(f"**Epic:** {epic_id} — {epic_theme}")
            lines.append(f"**Title:** {story.get('title', 'Untitled')}")
            lines.append("")
            lines.append(f"**As a** {story.get('as_a', 'user')}")
            lines.append(f"**I want** {story.get('i_want', 'this feature')}")
            lines.append(f"**So that** {story.get('so_that', 'I can benefit')}")
            lines.append("")
            lines.append("**Acceptance criteria:**")
            for ac in story.get("acceptance_criteria", []):
                lines.append(f"- {ac}")
            lines.append("")
            lines.append("**Sources:**")
            for src in story.get("sources", []):
                if isinstance(src, dict):
                    file_ref = src.get("file", "unknown")
                    line_ref = src.get("lines", "")
                    ref = f"`{file_ref}:{line_ref}`" if line_ref else f"`{file_ref}`"
                    lines.append(f"- {ref}")
                elif isinstance(src, str):
                    lines.append(f"- `{src}`")
            lines.append("")
            lines.append("**Status:** pending")
            lines.append("")

    return "\n".join(lines)


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: aggregate_stories.py <json-file>...", file=sys.stderr)
        return 2

    paths = [Path(p) for p in sys.argv[1:]]
    for p in paths:
        if not p.exists():
            print(f"error: file not found: {p}", file=sys.stderr)
            return 2

    stories = load_stories(paths)
    if not stories:
        print("error: no stories found in input files", file=sys.stderr)
        return 1

    deduped = dedup_stories(stories)
    epics = group_into_epics(deduped)
    output = format_requirements_index(epics)
    print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
