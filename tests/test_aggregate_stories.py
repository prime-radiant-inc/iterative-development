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

    def test_no_input_returns_error(self):
        result = subprocess.run(
            ["python3", str(SCRIPT)],
            capture_output=True, text=True,
        )
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
