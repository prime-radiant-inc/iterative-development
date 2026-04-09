"""Unit tests for extracting-requirements/scripts/aggregate_stories.py."""
import json
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "skills" / "extracting-requirements" / "scripts" / "aggregate_stories.py"
FIXTURES = Path(__file__).parent / "fixtures"
VALIDATOR = Path(__file__).parent.parent / "skills" / "extracting-requirements" / "scripts" / "validate_requirements_index.py"


class TestAggregateStories(unittest.TestCase):
    def setUp(self):
        self.out_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.out_dir, ignore_errors=True)

    def _run(self, *extra_args):
        return subprocess.run(
            ["python3", str(SCRIPT), "-o", str(self.out_dir), *extra_args],
            capture_output=True, text=True,
        )

    def _read_all(self) -> str:
        """Read all .md files in output dir concatenated."""
        parts = []
        for f in sorted(self.out_dir.glob("*.md")):
            parts.append(f.read_text())
        return "\n".join(parts)

    def test_script_exists(self):
        self.assertTrue(SCRIPT.exists())

    def test_sample_fixture_produces_valid_output(self):
        """Aggregating the sample fixture should produce valid per-epic files."""
        result = self._run(str(FIXTURES / "extracted-stories-sample.json"))
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        # Should create epic files
        epic_files = list(self.out_dir.glob("EPIC-*.md"))
        self.assertGreater(len(epic_files), 0)
        # Validate the output directory
        val_result = subprocess.run(
            ["python3", str(VALIDATOR), str(self.out_dir)],
            capture_output=True, text=True,
        )
        self.assertEqual(val_result.returncode, 0,
                         msg=f"Validator failed: {val_result.stderr}")

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
            result = self._run(tmp)
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            output = self._read_all()
            # Should have exactly ONE STORY (deduped)
            self.assertEqual(output.count("## STORY-"), 1)
            # But should cite both sources
            self.assertIn("a.md", output)
            self.assertIn("b.md", output)
        finally:
            Path(tmp).unlink()

    def test_epics_grouped_into_separate_files(self):
        """Stories with different epic_themes get separate files."""
        result = self._run(str(FIXTURES / "extracted-stories-sample.json"))
        # Sample has 2 themes: "Task Management" and "Billing"
        epic_files = sorted(self.out_dir.glob("EPIC-*.md"))
        self.assertEqual(len(epic_files), 2)

    def test_story_ids_are_sequential(self):
        """Story IDs should be assigned sequentially starting from 0001."""
        self._run(str(FIXTURES / "extracted-stories-sample.json"))
        output = self._read_all()
        story_ids = re.findall(r"## STORY-(\d+)", output)
        self.assertEqual(story_ids, ["0001", "0002", "0003", "0004", "0005"])

    def test_no_input_returns_error(self):
        result = subprocess.run(
            ["python3", str(SCRIPT)],
            capture_output=True, text=True,
        )
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
