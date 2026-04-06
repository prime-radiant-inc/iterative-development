#!/usr/bin/env bash
# Validation suite for the iterative-development plugin.
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
echo "=== Verifying extraction pipeline scripts ==="
python3 scripts/chunk_spec.py tests/fixtures/multi-file-spec/ > /dev/null
echo "OK: chunk_spec.py runs on multi-file-spec fixture"
python3 scripts/aggregate_stories.py tests/fixtures/extracted-stories-sample.json > /dev/null
echo "OK: aggregate_stories.py runs on sample fixture"

echo ""
echo "=== Verifying citation checker ==="
python3 scripts/check_citations.py tests/fixtures/roadmap.example.md tests/fixtures/requirements-index.example.md
test -f skills/running-an-iteration/scope-reviewer-prompt.md && echo "OK: scope-reviewer-prompt.md exists" || { echo "FAIL: scope-reviewer-prompt.md missing"; exit 1; }

echo ""
echo "=== Verifying PAR reference documents ==="
for par_file in skills/shared/*.md; do
    test -f "$par_file" && echo "OK: $par_file exists" || { echo "FAIL: $par_file missing"; exit 1; }
done
test -f skills/auditing-progress/auditor-subagent-prompt.md && echo "OK: auditor-subagent-prompt.md exists" || { echo "FAIL: auditor-subagent-prompt.md missing"; exit 1; }

echo ""
echo "=== All validation checks passed ==="
