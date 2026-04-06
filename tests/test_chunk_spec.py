"""Unit tests for scripts/chunk_spec.py."""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "scripts" / "chunk_spec.py"


class TestChunkSpec(unittest.TestCase):
    def test_script_exists(self):
        self.assertTrue(SCRIPT.exists())

    def test_small_file_is_single_chunk(self):
        """A file under the token threshold should produce exactly one chunk."""
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
            f.write("# Small Spec\n\nJust a few words here.\n")
            tmp = f.name
        try:
            result = subprocess.run(
                ["python3", str(SCRIPT), tmp],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            chunks = json.loads(result.stdout)
            self.assertEqual(len(chunks), 1)
            self.assertIn("Small Spec", chunks[0]["content"])
            self.assertEqual(chunks[0]["source_file"], tmp)
        finally:
            Path(tmp).unlink()

    def test_file_with_headings_splits_by_h2(self):
        """A file over the token threshold with ## headings should split by heading."""
        # Create content big enough to trigger splitting (>3K words ≈ >4K tokens)
        section_a = "## Section A\n\n" + ("word " * 2000) + "\n\n"
        section_b = "## Section B\n\n" + ("word " * 2000) + "\n\n"
        content = "# Big Spec\n\nPreamble text.\n\n" + section_a + section_b

        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
            f.write(content)
            tmp = f.name
        try:
            result = subprocess.run(
                ["python3", str(SCRIPT), tmp, "--max-tokens", "3000"],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            chunks = json.loads(result.stdout)
            # Should have preamble + Section A + Section B = 3 chunks
            self.assertGreaterEqual(len(chunks), 2)
            headings = [c["heading"] for c in chunks]
            self.assertIn("Section A", headings)
            self.assertIn("Section B", headings)
        finally:
            Path(tmp).unlink()

    def test_directory_processes_all_md_files(self):
        """A directory should produce chunks from all .md files in it."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "a.md").write_text("# File A\n\nContent A.\n")
            (Path(tmpdir) / "b.md").write_text("# File B\n\nContent B.\n")
            (Path(tmpdir) / "c.txt").write_text("Not markdown, should be ignored.\n")

            result = subprocess.run(
                ["python3", str(SCRIPT), tmpdir],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            chunks = json.loads(result.stdout)
            source_files = {c["source_file"] for c in chunks}
            self.assertEqual(len(source_files), 2)  # only .md files
            self.assertTrue(all("Content" in c["content"] for c in chunks))

    def test_missing_path_returns_error(self):
        result = subprocess.run(
            ["python3", str(SCRIPT), "/tmp/does-not-exist-99999"],
            capture_output=True, text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not found", result.stderr.lower())

    def test_each_chunk_has_required_fields(self):
        """Every chunk must have source_file, heading, start_line, end_line, content, estimated_tokens."""
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
            f.write("# Test\n\nHello world.\n")
            tmp = f.name
        try:
            result = subprocess.run(
                ["python3", str(SCRIPT), tmp],
                capture_output=True, text=True,
            )
            chunks = json.loads(result.stdout)
            for chunk in chunks:
                for field in ("source_file", "heading", "start_line", "end_line",
                              "content", "estimated_tokens"):
                    self.assertIn(field, chunk, f"missing field: {field}")
        finally:
            Path(tmp).unlink()


if __name__ == "__main__":
    unittest.main()
