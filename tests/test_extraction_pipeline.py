"""Integration test for the extraction pipeline.

Tests: chunk multi-file spec → [sample extraction output] → aggregate → validate.
The extraction step (LLM dispatch) is replaced by a pre-extracted fixture.
"""
import json
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

EXTRACT_SCRIPTS = Path(__file__).parent.parent / "skills" / "extracting-requirements" / "scripts"
FIXTURES = Path(__file__).parent / "fixtures"


class TestExtractionPipeline(unittest.TestCase):
    def setUp(self):
        self.out_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.out_dir, ignore_errors=True)

    def test_chunk_then_aggregate_produces_valid_output(self):
        """Full pipeline: chunk the multi-file spec, aggregate the sample output, validate."""
        # Step 1: Chunk the multi-file spec (verifies chunking works on fixture)
        chunk_result = subprocess.run(
            ["python3", str(EXTRACT_SCRIPTS / "chunk_spec.py"),
             str(FIXTURES / "multi-file-spec")],
            capture_output=True, text=True,
        )
        self.assertEqual(chunk_result.returncode, 0, msg=chunk_result.stderr)
        chunks = json.loads(chunk_result.stdout)
        self.assertGreaterEqual(len(chunks), 3, "Expected at least 3 chunks from 3 files")

        # Step 2: Aggregate the sample extraction output (simulates what subagents return)
        agg_result = subprocess.run(
            ["python3", str(EXTRACT_SCRIPTS / "aggregate_stories.py"),
             "-o", str(self.out_dir),
             str(FIXTURES / "extracted-stories-sample.json")],
            capture_output=True, text=True,
        )
        self.assertEqual(agg_result.returncode, 0, msg=agg_result.stderr)

        # Step 3: Validate the aggregated output directory
        val_result = subprocess.run(
            ["python3", str(EXTRACT_SCRIPTS / "validate_requirements_index.py"),
             str(self.out_dir)],
            capture_output=True, text=True,
        )
        self.assertEqual(val_result.returncode, 0,
                         msg=f"Validator failed on aggregated output: {val_result.stderr}")

    def test_aggregated_output_has_correct_story_count(self):
        """Sample fixture has 5 stories — aggregation should produce 5 STORY headers."""
        subprocess.run(
            ["python3", str(EXTRACT_SCRIPTS / "aggregate_stories.py"),
             "-o", str(self.out_dir),
             str(FIXTURES / "extracted-stories-sample.json")],
            capture_output=True, text=True,
        )
        all_content = "\n".join(f.read_text() for f in sorted(self.out_dir.glob("*.md")))
        story_count = len(re.findall(r"^## STORY-\d+$", all_content, re.MULTILINE))
        self.assertEqual(story_count, 5, f"Expected 5 stories, got {story_count}")

    def test_aggregated_output_has_correct_epic_count(self):
        """Sample fixture has 2 epic themes — aggregation should produce 2 epic files."""
        subprocess.run(
            ["python3", str(EXTRACT_SCRIPTS / "aggregate_stories.py"),
             "-o", str(self.out_dir),
             str(FIXTURES / "extracted-stories-sample.json")],
            capture_output=True, text=True,
        )
        epic_files = list(self.out_dir.glob("EPIC-*.md"))
        self.assertEqual(len(epic_files), 2, f"Expected 2 epic files, got {len(epic_files)}")


if __name__ == "__main__":
    unittest.main()
