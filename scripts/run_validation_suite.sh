#!/usr/bin/env bash
# Walking skeleton validation suite.
# Runs all unit tests and validators. Fails on first error.
set -euo pipefail

cd "$(dirname "$0")/.."

echo "=== Running Python unit tests ==="
python3 -m unittest discover tests/ -v

echo ""
echo "=== Validating plugin manifest ==="
python3 -c "import json; json.load(open('.claude-plugin/plugin.json'))"
echo "OK: .claude-plugin/plugin.json"

echo ""
echo "=== Validating all SKILL.md files ==="
for skill_file in skills/*/SKILL.md; do
    python3 scripts/validate_skill.py "$skill_file"
done

echo ""
echo "=== Validating artifact format fixtures ==="
python3 scripts/validate_artifact.py --type requirements-index tests/fixtures/requirements-index.example.md
python3 scripts/validate_artifact.py --type roadmap tests/fixtures/roadmap.example.md
python3 scripts/validate_artifact.py --type iteration-log tests/fixtures/iteration-log.example.md

echo ""
echo "=== All validation checks passed ==="
