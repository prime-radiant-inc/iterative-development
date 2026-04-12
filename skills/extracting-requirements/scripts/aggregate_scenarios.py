#!/usr/bin/env python3
"""Aggregate extracted scenario JSONs into behavior-scenarios.md.

Usage: aggregate_scenarios.py -o <output-file> --stories-dir <requirements-dir> <json-file>...

Takes one or more JSON files (each containing {"scenarios": [...]}),
deduplicates by title, assigns stable IDs (SCENARIO-NNNN for surface,
JOURNEY-NNNN for journey), resolves owning_story_titles to STORY-IDs
using the requirements directory, and writes behavior-scenarios.md.
"""
import argparse
import json
import re
import sys
from collections import OrderedDict
from pathlib import Path


def load_scenarios(paths: list[Path]) -> list[dict]:
    """Load and combine scenarios from multiple JSON files."""
    all_scenarios: list[dict] = []
    for p in paths:
        data = json.loads(p.read_text())
        if isinstance(data, dict) and "scenarios" in data:
            all_scenarios.extend(data["scenarios"])
        elif isinstance(data, list):
            all_scenarios.extend(data)
    return all_scenarios


def load_story_title_to_id(stories_dir: Path) -> dict[str, str]:
    """Build a title -> STORY-ID map from per-epic requirement files."""
    title_map: dict[str, str] = {}
    for epic_file in sorted(stories_dir.glob("EPIC-*.md")):
        text = epic_file.read_text()
        current_id = None
        for line in text.splitlines():
            id_match = re.match(r"^## (STORY-\d+)", line)
            if id_match:
                current_id = id_match.group(1)
            title_match = re.match(r"\*\*Title:\*\* (.+)", line)
            if title_match and current_id:
                title_map[title_match.group(1).strip()] = current_id
                current_id = None
    return title_map


def dedup_scenarios(scenarios: list[dict]) -> list[dict]:
    """Deduplicate scenarios by exact title match."""
    seen: dict[str, dict] = OrderedDict()
    for scenario in scenarios:
        title = scenario.get("title", "").strip()
        if title not in seen:
            seen[title] = dict(scenario)
        else:
            # Merge owning_story_titles and sources
            existing = seen[title]
            for t in scenario.get("owning_story_titles", []):
                if t not in existing.get("owning_story_titles", []):
                    existing.setdefault("owning_story_titles", []).append(t)
            for s in scenario.get("sources", []):
                if s not in existing.get("sources", []):
                    existing.setdefault("sources", []).append(s)
    return list(seen.values())


def assign_ids(scenarios: list[dict]) -> None:
    """Assign stable SCENARIO-NNNN or JOURNEY-NNNN IDs."""
    scenario_counter = 1
    journey_counter = 1
    for s in scenarios:
        if s.get("kind") == "journey":
            s["_id"] = f"JOURNEY-{journey_counter:04d}"
            journey_counter += 1
        else:
            s["_id"] = f"SCENARIO-{scenario_counter:04d}"
            scenario_counter += 1


def resolve_story_refs(scenarios: list[dict], title_map: dict[str, str]) -> None:
    """Replace owning_story_titles with resolved STORY-IDs where possible."""
    for s in scenarios:
        resolved = []
        for title in s.get("owning_story_titles", []):
            story_id = title_map.get(title.strip())
            if story_id:
                resolved.append(story_id)
            else:
                resolved.append(f"UNRESOLVED({title})")
        s["_owning_stories"] = resolved


def format_scenario(s: dict) -> str:
    """Format one scenario as markdown."""
    lines: list[str] = []
    sid = s["_id"]
    title = s.get("title", "Untitled")
    lines.append(f"## {sid} — {title}")
    lines.append("")

    kind = s.get("kind", "surface")
    seam = s.get("proof_seam", "unknown")
    stories = ", ".join(s.get("_owning_stories", []))

    if kind == "journey":
        lines.append(f"**Kind:** journey")
        lines.append(f"**Proof seam:** e2e")
    else:
        lines.append(f"**Kind:** {kind}")
        lines.append(f"**Proof seam:** {seam}")

    lines.append(f"**Owning stories:** {stories}")
    lines.append("")

    lines.append("**Preconditions:**")
    for p in s.get("preconditions", []):
        lines.append(f"- {p}")
    lines.append("")

    if kind == "journey":
        lines.append("**Steps:**")
        for i, step in enumerate(s.get("steps", []), 1):
            action = step.get("action", "")
            lines.append(f"{i}. {action}")
            for exp in step.get("expected", []):
                lines.append(f"   → {exp}")
        lines.append("")
        lines.append("**Final observables:**")
        for obs in s.get("final_observables", []):
            lines.append(f"- {obs}")
    else:
        lines.append("**Action:**")
        for step in s.get("steps", []):
            lines.append(f"- {step.get('action', '')}")
        lines.append("")
        lines.append("**Expected observables:**")
        for step in s.get("steps", []):
            for exp in step.get("expected", []):
                lines.append(f"- {exp}")
        for obs in s.get("final_observables", []):
            lines.append(f"- {obs}")
    lines.append("")

    lines.append("**Automation status:** pending")
    lines.append("**Execution command:** TBD")
    lines.append("")

    lines.append("**Sources:**")
    for src in s.get("sources", []):
        if isinstance(src, dict):
            f = src.get("file", "")
            l = src.get("lines", "")
            lines.append(f"- `{f}:{l}`" if l else f"- `{f}`")
        elif isinstance(src, str):
            lines.append(f"- `{src}`")
    lines.append("")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Aggregate scenarios into behavior-scenarios.md")
    parser.add_argument("-o", "--output", required=True, help="Output file path")
    parser.add_argument("--stories-dir", required=True,
                        help="Requirements directory for resolving story title -> ID")
    parser.add_argument("json_files", nargs="+", help="Extracted scenario JSON files")
    args = parser.parse_args()

    paths = [Path(p) for p in args.json_files]
    for p in paths:
        if not p.exists():
            print(f"error: file not found: {p}", file=sys.stderr)
            return 2

    stories_dir = Path(args.stories_dir)
    if not stories_dir.is_dir():
        print(f"error: stories directory not found: {stories_dir}", file=sys.stderr)
        return 2

    scenarios = load_scenarios(paths)
    if not scenarios:
        print("warning: no scenarios found in input files", file=sys.stderr)
        Path(args.output).write_text("# Behavior Scenarios\n\nNo scenarios extracted.\n")
        return 0

    deduped = dedup_scenarios(scenarios)
    assign_ids(deduped)

    title_map = load_story_title_to_id(stories_dir)
    resolve_story_refs(deduped, title_map)

    # Separate journeys and surface scenarios
    journeys = [s for s in deduped if s.get("kind") == "journey"]
    surfaces = [s for s in deduped if s.get("kind") != "journey"]

    lines: list[str] = ["# Behavior Scenarios", ""]

    if journeys:
        lines.append("## Journey Scenarios")
        lines.append("")
        for s in journeys:
            lines.append(format_scenario(s))

    if surfaces:
        lines.append("## Surface Scenarios")
        lines.append("")
        for s in surfaces:
            lines.append(format_scenario(s))

    Path(args.output).write_text("\n".join(lines))

    print(f"OK: {len(journeys)} journey scenarios, {len(surfaces)} surface scenarios")
    return 0


if __name__ == "__main__":
    sys.exit(main())
