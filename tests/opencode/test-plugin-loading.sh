#!/usr/bin/env bash
# Test: Plugin Loading
# Verifies that the iterative-development plugin package has the structure OpenCode needs.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== Test: Plugin Loading ==="

source "$SCRIPT_DIR/setup.sh"
trap cleanup_test_env EXIT

plugin_link="$OPENCODE_CONFIG_DIR/plugins/iterative-development.js"

echo "Test 1: Checking plugin registration..."
if [ -L "$plugin_link" ]; then
    echo "  [PASS] Plugin symlink exists"
else
    echo "  [FAIL] Plugin symlink not found at $plugin_link"
    exit 1
fi

plugin_target=$(python3 -c 'import os, sys; print(os.path.realpath(sys.argv[1]))' "$plugin_link")
if [ -f "$plugin_target" ]; then
    echo "  [PASS] Plugin symlink target exists"
else
    echo "  [FAIL] Plugin symlink target does not exist"
    exit 1
fi

echo "Test 2: Checking skills directory..."
skill_count=$(find "$ITERATIVE_DEVELOPMENT_SKILLS_DIR" -name "SKILL.md" | wc -l)
if [ "$skill_count" -eq 6 ]; then
    echo "  [PASS] Found all 6 iterative-development skills"
else
    echo "  [FAIL] Expected 6 skills, found $skill_count"
    exit 1
fi

echo "Test 3: Checking top-level skill exists..."
if [ -f "$ITERATIVE_DEVELOPMENT_SKILLS_DIR/iterative-development/SKILL.md" ]; then
    echo "  [PASS] iterative-development skill exists"
else
    echo "  [FAIL] iterative-development skill not found"
    exit 1
fi

echo "Test 4: Checking plugin JavaScript syntax..."
if node --check "$ITERATIVE_DEVELOPMENT_PLUGIN_FILE" 2>/dev/null; then
    echo "  [PASS] Plugin JavaScript syntax is valid"
else
    echo "  [FAIL] Plugin has JavaScript syntax errors"
    exit 1
fi

echo "Test 5: Checking package metadata..."
python3 - <<'PY'
import json
from pathlib import Path

data = json.loads(Path('package.json').read_text())
assert data['name'] == 'iterative-development'
assert data['type'] == 'module'
assert data['main'] == '.opencode/plugins/iterative-development.js'
PY
echo "  [PASS] package.json points to OpenCode plugin"

echo ""
echo "=== All plugin loading tests passed ==="
