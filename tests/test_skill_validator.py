"""Unit tests for scripts/validate_skill.py."""
import subprocess
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "scripts" / "validate_skill.py"
FIXTURES = Path(__file__).parent / "fixtures"


class TestSkillValidator(unittest.TestCase):
    def test_script_exists(self):
        self.assertTrue(SCRIPT.exists())

    def test_valid_skill_passes(self):
        result = subprocess.run(
            ["python3", str(SCRIPT), str(FIXTURES / "skill.valid" / "SKILL.md")],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)

    def test_missing_frontmatter_fails(self):
        result = subprocess.run(
            ["python3", str(SCRIPT),
             str(FIXTURES / "skill.invalid-no-frontmatter" / "SKILL.md")],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("frontmatter", result.stderr.lower())

    def test_bad_description_format_fails(self):
        result = subprocess.run(
            ["python3", str(SCRIPT),
             str(FIXTURES / "skill.invalid-bad-description" / "SKILL.md")],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("use when", result.stderr.lower())


if __name__ == "__main__":
    unittest.main()
