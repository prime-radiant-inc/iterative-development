"""Unit tests for scripts/aggregate_stories.py."""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "scripts" / "aggregate_stories.py"
FIXTURES = Path(__file__).parent / "fixtures"
VALIDATOR = Path(__file__).parent.parent / "scripts" / "validate_artifact.py"


class TestAggregateStories(unittest.TestCase):
    def test_script_exists(self):
        self.assertTrue(SCRIPT.exists())

    def test_sample_fixture_produces_valid_index(self):
        """Aggregating the sample fixture should produce a valid requirements-index.md."""
        result = subprocess.run(
            ["python3", str(SCRIPT), str(FIXTURES / "extracted-stories-sample.json")],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        output = result.stdout
        # Should contain story and epic headers
        self.assertIn("## STORY-0001", output)
        self.assertIn("## EPIC-", output)
        # Validate the output with the artifact validator
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
            f.write(output)
            tmp = f.name
        try:
            val_result = subprocess.run(
                ["python3", str(VALIDATOR), "--type", "requirements-index", tmp],
                capture_output=True, text=True,
            )
            self.assertEqual(val_result.returncode, 0,
                             msg=f"Validator failed: {val_result.stderr}")
        finally:
            Path(tmp).unlink()

    def test_dedup_merges_duplicate_titles(self):
        """Stories with identical titles should be merged, sources combined."""
        stories = [
            {
                "title": "Same Story",
                "epic_theme": "Test",
                "as_a": "user", "i_want": "x", "so_that": "y",
                "acceptance_criteria": ["AC-1: test"],
                "sources": [{"file": "a.md", "lines": "1-5"}]
            },
            {
                "title": "Same Story",
                "epic_theme": "Test",
                "as_a": "user", "i_want": "x", "so_that": "y",
                "acceptance_criteria": ["AC-1: test"],
                "sources": [{"file": "b.md", "lines": "10-15"}]
            },
        ]
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump(stories, f)
            tmp = f.name
        try:
            result = subprocess.run(
                ["python3", str(SCRIPT), tmp],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            output = result.stdout
            # Should have exactly ONE STORY (deduped)
            self.assertEqual(output.count("## STORY-"), 1)
            # But should cite both sources
            self.assertIn("a.md", output)
            self.assertIn("b.md", output)
        finally:
            Path(tmp).unlink()

    def test_epics_grouped_by_theme(self):
        """Stories with different epic_themes get different EPIC IDs."""
        result = subprocess.run(
            ["python3", str(SCRIPT), str(FIXTURES / "extracted-stories-sample.json")],
            capture_output=True, text=True,
        )
        output = result.stdout
        # Sample has 2 themes: "Task Management" (3 stories) and "Billing" (2 stories)
        self.assertIn("Task Management", output)
        self.assertIn("Billing", output)
        # Should have 2 epics
        import re
        epic_ids = re.findall(r"## EPIC-\d+", output)
        self.assertEqual(len(epic_ids), 2)

    def test_story_ids_are_sequential(self):
        """Story IDs should be assigned sequentially starting from 0001."""
        result = subprocess.run(
            ["python3", str(SCRIPT), str(FIXTURES / "extracted-stories-sample.json")],
            capture_output=True, text=True,
        )
        import re
        story_ids = re.findall(r"## STORY-(\d+)", result.stdout)
        self.assertEqual(story_ids, ["0001", "0002", "0003", "0004", "0005"])

    def test_child_themes_merge_into_parent(self):
        """'Parent - Child' epic themes should merge into the parent epic."""
        stories = [
            {
                "title": "Pipeline starts",
                "epic_theme": "Recording Pipeline",
                "as_a": "user", "i_want": "x", "so_that": "y",
                "acceptance_criteria": ["AC-1: starts"],
                "sources": [{"file": "a.md", "lines": "1-5"}]
            },
            {
                "title": "Pipeline state machine",
                "epic_theme": "Recording Pipeline - State Machine",
                "as_a": "user", "i_want": "x", "so_that": "y",
                "acceptance_criteria": ["AC-1: state"],
                "sources": [{"file": "b.md", "lines": "1-5"}]
            },
            {
                "title": "Pipeline concurrency",
                "epic_theme": "Recording Pipeline - Concurrency",
                "as_a": "user", "i_want": "x", "so_that": "y",
                "acceptance_criteria": ["AC-1: concurrency"],
                "sources": [{"file": "c.md", "lines": "1-5"}]
            },
            {
                "title": "Unrelated feature",
                "epic_theme": "CLI",
                "as_a": "user", "i_want": "x", "so_that": "y",
                "acceptance_criteria": ["AC-1: cli"],
                "sources": [{"file": "d.md", "lines": "1-5"}]
            },
        ]
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump(stories, f)
            tmp = f.name
        try:
            result = subprocess.run(
                ["python3", str(SCRIPT), tmp],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            output = result.stdout
            import re
            epic_headers = re.findall(r"## (EPIC-\d+) — (.+)", output)
            theme_names = [name for _, name in epic_headers]
            # Should have 2 epics: "Recording Pipeline" and "CLI"
            # NOT 4 epics with separate "Recording Pipeline - State Machine" etc.
            self.assertEqual(len(epic_headers), 2, f"Expected 2 epics, got: {theme_names}")
            self.assertIn("Recording Pipeline", theme_names)
            self.assertIn("CLI", theme_names)
            # All 3 recording stories should be under the same epic
            recording_epic = [eid for eid, name in epic_headers if name == "Recording Pipeline"][0]
            story_epic_refs = re.findall(rf"\*\*Epic:\*\* {recording_epic}", output)
            self.assertEqual(len(story_epic_refs), 3,
                             f"Expected 3 stories under {recording_epic}")
        finally:
            Path(tmp).unlink()

    def test_orphan_child_themes_create_parent(self):
        """'Parent - Child' themes with no standalone parent should still merge."""
        stories = [
            {
                "title": "Persist prefs",
                "epic_theme": "Data Persistence - Preferences",
                "as_a": "user", "i_want": "x", "so_that": "y",
                "acceptance_criteria": ["AC-1: prefs"],
                "sources": [{"file": "a.md", "lines": "1-5"}]
            },
            {
                "title": "Persist audio",
                "epic_theme": "Data Persistence - Audio",
                "as_a": "user", "i_want": "x", "so_that": "y",
                "acceptance_criteria": ["AC-1: audio"],
                "sources": [{"file": "b.md", "lines": "1-5"}]
            },
        ]
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump(stories, f)
            tmp = f.name
        try:
            result = subprocess.run(
                ["python3", str(SCRIPT), tmp],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            output = result.stdout
            import re
            epic_headers = re.findall(r"## (EPIC-\d+) — (.+)", output)
            theme_names = [name for _, name in epic_headers]
            # Should create one "Data Persistence" parent epic
            self.assertEqual(len(epic_headers), 1, f"Expected 1 epic, got: {theme_names}")
            self.assertIn("Data Persistence", theme_names)
        finally:
            Path(tmp).unlink()

    def test_no_input_returns_error(self):
        result = subprocess.run(
            ["python3", str(SCRIPT)],
            capture_output=True, text=True,
        )
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
