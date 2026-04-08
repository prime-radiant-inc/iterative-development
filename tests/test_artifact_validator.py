"""Unit tests for per-skill artifact validators."""
import subprocess
import unittest
from pathlib import Path

SKILLS = Path(__file__).parent.parent / "skills"
FIXTURES = Path(__file__).parent / "fixtures"

VALIDATE_REQ_INDEX = SKILLS / "extracting-requirements" / "scripts" / "validate_requirements_index.py"
VALIDATE_ROADMAP = SKILLS / "scoping-the-simplest-core" / "scripts" / "validate_roadmap.py"
VALIDATE_ITER_LOG = SKILLS / "running-an-iteration" / "scripts" / "validate_iteration_log.py"


class TestRequirementsIndexValidator(unittest.TestCase):
    def test_script_exists(self):
        self.assertTrue(VALIDATE_REQ_INDEX.exists())

    def test_valid_example_passes(self):
        result = subprocess.run(
            ["python3", str(VALIDATE_REQ_INDEX),
             str(FIXTURES / "requirements-index.example.md")],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)

    def test_invalid_example_fails(self):
        result = subprocess.run(
            ["python3", str(VALIDATE_REQ_INDEX),
             str(FIXTURES / "requirements-index.invalid.md")],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 1)

    def test_missing_story_id_is_flagged(self):
        import tempfile, os
        content = (FIXTURES / "requirements-index.example.md").read_text()
        broken = content.replace("## STORY-0001", "## STORY-")
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
            f.write(broken)
            tmp = f.name
        try:
            result = subprocess.run(
                ["python3", str(VALIDATE_REQ_INDEX), tmp],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("story id", result.stderr.lower())
        finally:
            os.unlink(tmp)

    def test_missing_file_returns_nonzero(self):
        result = subprocess.run(
            ["python3", str(VALIDATE_REQ_INDEX), "/tmp/does-not-exist-12345.md"],
            capture_output=True, text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not found", result.stderr.lower())


class TestRoadmapValidator(unittest.TestCase):
    def test_script_exists(self):
        self.assertTrue(VALIDATE_ROADMAP.exists())

    def test_valid_example_passes(self):
        result = subprocess.run(
            ["python3", str(VALIDATE_ROADMAP),
             str(FIXTURES / "roadmap.example.md")],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)

    def test_invalid_example_fails(self):
        result = subprocess.run(
            ["python3", str(VALIDATE_ROADMAP),
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
                ["python3", str(VALIDATE_ROADMAP), tmp],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("walking skeleton", result.stderr.lower())
        finally:
            os.unlink(tmp)


class TestIterationLogValidator(unittest.TestCase):
    def test_script_exists(self):
        self.assertTrue(VALIDATE_ITER_LOG.exists())

    def test_valid_example_passes(self):
        result = subprocess.run(
            ["python3", str(VALIDATE_ITER_LOG),
             str(FIXTURES / "iteration-log.example.md")],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)

    def test_invalid_example_fails(self):
        result = subprocess.run(
            ["python3", str(VALIDATE_ITER_LOG),
             str(FIXTURES / "iteration-log.invalid.md")],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 1)


if __name__ == "__main__":
    unittest.main()
