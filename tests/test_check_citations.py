"""Unit tests for scripts/check_citations.py."""
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "scripts" / "check_citations.py"
FIXTURES = Path(__file__).parent / "fixtures"


class TestCheckCitations(unittest.TestCase):
    def test_script_exists(self):
        self.assertTrue(SCRIPT.exists())

    def test_valid_fixtures_pass(self):
        """The example roadmap cites STORY-0001 which exists in the example index."""
        result = subprocess.run(
            ["python3", str(SCRIPT),
             str(FIXTURES / "roadmap.example.md"),
             str(FIXTURES / "requirements-index.example.md")],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)

    def test_missing_story_is_flagged(self):
        """A roadmap citing a story that doesn't exist should fail."""
        import os
        roadmap = "# Roadmap\n\n## Walking skeleton (ITER-0000)\n\n**Intent:** test\n**Stories committed:**\n- STORY-9999 (EPIC-001)\n**Status:** pending\n\n## Iteration list\n"
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
            f.write(roadmap)
            tmp_roadmap = f.name
        try:
            result = subprocess.run(
                ["python3", str(SCRIPT), tmp_roadmap,
                 str(FIXTURES / "requirements-index.example.md")],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("STORY-9999", result.stderr)
        finally:
            os.unlink(tmp_roadmap)

    def test_missing_file_returns_error(self):
        result = subprocess.run(
            ["python3", str(SCRIPT), "/tmp/no-such-file.md", "/tmp/no-such-index.md"],
            capture_output=True, text=True,
        )
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
