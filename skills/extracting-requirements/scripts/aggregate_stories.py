#!/usr/bin/env python3
"""Aggregate extracted story card JSONs into per-epic requirement files.

Usage: aggregate_stories.py -o <output-dir> <json-file>...

Takes one or more JSON files (each a list of story objects or {"stories": [...]}),
deduplicates by title, groups into epics by epic_theme, assigns stable IDs
(STORY-NNNN, EPIC-NNN), and writes one file per epic to the output directory.
"""
import argparse
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


def assign_ids(epics: dict[str, list[dict]]) -> None:
    """Assign stable EPIC-NNN and STORY-NNNN IDs to all stories in place."""
    story_counter = 1
    epic_counter = 1
    for theme, stories in epics.items():
        epic_id = f"EPIC-{epic_counter:03d}"
        epic_counter += 1
        for story in stories:
            story["_id"] = f"STORY-{story_counter:04d}"
            story["_epic_id"] = epic_id
            story["_epic_theme"] = theme
            story_counter += 1


def format_epic_file(epic_id: str, theme: str, stories: list[dict]) -> str:
    """Format one epic as a standalone markdown file."""
    lines: list[str] = []

    story_ids = [s["_id"] for s in stories]

    primary_sources: set[str] = set()
    for s in stories:
        for src in s.get("sources", []):
            if isinstance(src, dict):
                primary_sources.add(src.get("file", ""))
            elif isinstance(src, str):
                primary_sources.add(src)

    lines.append(f"# {epic_id} — {theme}")
    lines.append("")
    lines.append(f"**Summary:** {theme}")
    lines.append(f"**Stories:** {', '.join(story_ids)}")
    if primary_sources:
        sources_str = ", ".join(f"`{s}`" for s in sorted(primary_sources) if s)
        lines.append(f"**Primary sources:** {sources_str}")
    lines.append(f"**Status:** 0/{len(stories)} done")
    lines.append("")

    for story in stories:
        lines.append(f"## {story['_id']}")
        lines.append("")
        lines.append(f"**Epic:** {story['_epic_id']} — {story['_epic_theme']}")
        lines.append(f"**Title:** {story.get('title', 'Untitled')}")
        lines.append("")
        lines.append(f"**As a** {story.get('as_a', 'user')}")
        lines.append(f"**I want** {story.get('i_want', 'this feature')}")
        lines.append(f"**So that** {story.get('so_that', 'I can benefit')}")
        lines.append("")
        lines.append("**Acceptance criteria:**")
        for ac in story.get("acceptance_criteria", []):
            if isinstance(ac, dict):
                ac_text = ac.get("text", "")
                ac_id = ac.get("id", "")
                impact = ac.get("behavioral_impact", "")
                seam = ac.get("proof_seam", "")
                line = f"- {ac_id}: {ac_text}"
                if impact:
                    line += f" · impact:`{impact}`"
                if seam:
                    line += f" · seam:`{seam}`"
                lines.append(line)
            else:
                # Legacy plain-string AC format
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
    parser = argparse.ArgumentParser(description="Aggregate stories into per-epic files")
    parser.add_argument("-o", "--output-dir", required=True,
                        help="Directory to write per-epic files (created if needed)")
    parser.add_argument("json_files", nargs="+", help="Extracted story JSON files")
    args = parser.parse_args()

    paths = [Path(p) for p in args.json_files]
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
    assign_ids(epics)

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for theme, epic_stories in epics.items():
        epic_id = epic_stories[0]["_epic_id"]
        content = format_epic_file(epic_id, theme, epic_stories)
        out_path = out_dir / f"{epic_id}.md"
        out_path.write_text(content)
        print(f"wrote {out_path} ({len(epic_stories)} stories)")

    total = sum(len(s) for s in epics.values())
    print(f"OK: {len(epics)} epics, {total} stories")
    return 0


if __name__ == "__main__":
    sys.exit(main())
