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


if __name__ == "__main__":
    unittest.main()
