"""Unit tests for scripts/validate_artifact.py."""
import subprocess
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "scripts" / "validate_artifact.py"


class TestValidatorScaffold(unittest.TestCase):
    def test_script_exists_and_is_executable(self):
        self.assertTrue(SCRIPT.exists(), f"{SCRIPT} does not exist")

    def test_unknown_type_returns_nonzero(self):
        result = subprocess.run(
            ["python3", str(SCRIPT), "--type", "bogus", "/dev/null"],
            capture_output=True, text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unknown artifact type", result.stderr.lower())

    def test_missing_file_returns_nonzero(self):
        result = subprocess.run(
            ["python3", str(SCRIPT), "--type", "requirements-index", "/tmp/does-not-exist-12345.md"],
            capture_output=True, text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not found", result.stderr.lower())


FIXTURES = Path(__file__).parent / "fixtures"


class TestRequirementsIndexValidator(unittest.TestCase):
    def test_valid_example_passes(self):
        result = subprocess.run(
            ["python3", str(SCRIPT), "--type", "requirements-index",
             str(FIXTURES / "requirements-index.example.md")],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)

    def test_invalid_example_fails(self):
        result = subprocess.run(
            ["python3", str(SCRIPT), "--type", "requirements-index",
             str(FIXTURES / "requirements-index.invalid.md")],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 1)

    def test_missing_story_id_is_flagged(self):
        # Valid example minus the STORY-0001 id
        import tempfile, os
        content = (FIXTURES / "requirements-index.example.md").read_text()
        broken = content.replace("## STORY-0001", "## STORY-")
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
            f.write(broken)
            tmp = f.name
        try:
            result = subprocess.run(
                ["python3", str(SCRIPT), "--type", "requirements-index", tmp],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("story id", result.stderr.lower())
        finally:
            os.unlink(tmp)


class TestRoadmapValidator(unittest.TestCase):
    def test_valid_example_passes(self):
        result = subprocess.run(
            ["python3", str(SCRIPT), "--type", "roadmap",
             str(FIXTURES / "roadmap.example.md")],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)

    def test_invalid_example_fails(self):
        result = subprocess.run(
            ["python3", str(SCRIPT), "--type", "roadmap",
             str(FIXTURES / "roadmap.invalid.md")],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 1)

    def test_missing_walking_skeleton_is_flagged(self):
        import tempfile, os
        content = (FIXTURES / "roadmap.example.md").read_text()
        broken = content.replace("## Walking skeleton (ITER-0000)", "## Other thing")
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
            f.write(broken)
            tmp = f.name
        try:
            result = subprocess.run(
                ["python3", str(SCRIPT), "--type", "roadmap", tmp],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("walking skeleton", result.stderr.lower())
        finally:
            os.unlink(tmp)


if __name__ == "__main__":
    unittest.main()
