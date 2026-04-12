#!/usr/bin/env python3
"""Back-link scenario IDs into story AC lines in per-epic requirement files.

Usage: backlink_scenarios.py <scenarios-file> <requirements-dir>

Reads behavior-scenarios.md to find scenario → owning-story mappings,
then updates AC lines in the per-epic files to append scenario refs.

Only modifies AC lines that don't already have a scenario: reference.
"""
import re
import sys
from pathlib import Path


def parse_scenario_to_stories(scenarios_path: Path) -> dict[str, list[str]]:
    """Parse behavior-scenarios.md. Returns {STORY-ID: [scenario IDs]}."""
    story_to_scenarios: dict[str, list[str]] = {}
    text = scenarios_path.read_text()

    current_id = None
    for line in text.splitlines():
        id_match = re.match(r"^## (SCENARIO-\d+|JOURNEY-\d+)", line)
        if id_match:
            current_id = id_match.group(1)

        if current_id and line.startswith("**Owning stories:**"):
            refs_text = line.split(":**", 1)[1].strip()
            story_ids = re.findall(r"STORY-\d+", refs_text)
            for sid in story_ids:
                story_to_scenarios.setdefault(sid, []).append(current_id)

    return story_to_scenarios


def backlink_epic_file(
    epic_path: Path,
    story_to_scenarios: dict[str, list[str]],
) -> tuple[int, int]:
    """Update AC lines in one epic file. Returns (lines_updated, lines_skipped)."""
    lines = epic_path.read_text().splitlines()
    updated = 0
    skipped = 0
    current_story_id = None
    new_lines: list[str] = []

    for line in lines:
        story_match = re.match(r"^## (STORY-\d+)", line)
        if story_match:
            current_story_id = story_match.group(1)

        # Check if this is an AC line for a story that has scenarios
        if (
            current_story_id
            and current_story_id in story_to_scenarios
            and re.match(r"^- AC-\d+:", line)
        ):
            if "scenario:" in line.lower():
                # Already has a scenario ref
                skipped += 1
            else:
                # Check if this AC has observable impact (not none)
                if "impact:`none`" not in line:
                    scenario_ids = story_to_scenarios[current_story_id]
                    # Append first matching scenario ref
                    line = f"{line} · scenario:`{scenario_ids[0]}`"
                    updated += 1

        new_lines.append(line)

    if updated > 0:
        epic_path.write_text("\n".join(new_lines))

    return updated, skipped


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

    story_to_scenarios = parse_scenario_to_stories(scenarios_path)
    if not story_to_scenarios:
        print("warning: no scenario-to-story mappings found", file=sys.stderr)
        return 0

    total_updated = 0
    total_skipped = 0

    for epic_file in sorted(requirements_dir.glob("EPIC-*.md")):
        updated, skipped = backlink_epic_file(epic_file, story_to_scenarios)
        if updated > 0:
            print(f"{epic_file.name}: {updated} AC(s) linked")
        total_updated += updated
        total_skipped += skipped

    print(f"OK: {total_updated} AC(s) linked, {total_skipped} already linked")
    return 0


if __name__ == "__main__":
    sys.exit(main())
