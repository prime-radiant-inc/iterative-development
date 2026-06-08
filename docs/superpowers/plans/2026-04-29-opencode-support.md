# OpenCode Support Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `iterative-development` installable and usable from OpenCode via the same package/plugin pattern used by `superpowers`.

**Architecture:** Add a zero-dependency OpenCode plugin entrypoint that registers this repository's bundled `skills/` directory through OpenCode's `config` hook. Add package metadata so OpenCode/Bun can resolve the plugin from git, then add installation docs and structural tests that mirror `superpowers` without copying its bootstrap injection behavior.

**Tech Stack:** OpenCode plugin API, ESM JavaScript, shell test scripts, existing Markdown `SKILL.md` files, existing Python validation suite.

---

## Reference Findings

`superpowers` OpenCode support currently consists of these required pieces:

- `package.json` with `"type": "module"` and `"main": ".opencode/plugins/superpowers.js"` so OpenCode/Bun can load the plugin from a git package.
- `.opencode/plugins/superpowers.js` exporting a plugin function and registering `path.resolve(__dirname, '../../skills')` into `config.skills.paths`.
- `.opencode/INSTALL.md`, `docs/README.opencode.md`, and `README.md` OpenCode install links.
- `tests/opencode/` structural tests that copy the plugin and skills into an isolated fake OpenCode config, then verify plugin file, skill files, and JavaScript syntax.
- Optional integration tests that require the real `opencode` binary.

`iterative-development` currently has portable `skills/*/SKILL.md` files and Claude plugin metadata, but lacks these OpenCode pieces:

- No `.opencode/` directory.
- No `package.json`.
- No OpenCode install docs.
- No OpenCode structural tests.
- `scripts/run_validation_suite.sh` validates only `.claude-plugin/plugin.json` plus skill/artifact fixtures.

## File Structure

- Create `package.json`: git package metadata and OpenCode entrypoint.
- Create `.opencode/plugins/iterative-development.js`: minimal plugin that registers bundled skills.
- Create `.opencode/INSTALL.md`: quick OpenCode install instructions.
- Create `docs/README.opencode.md`: full OpenCode usage and troubleshooting guide.
- Modify `README.md`: describe Claude Code and OpenCode installation paths.
- Create `tests/opencode/setup.sh`: isolated fake OpenCode install layout for tests.
- Create `tests/opencode/test-plugin-loading.sh`: structural plugin loading test.
- Create `tests/opencode/run-tests.sh`: OpenCode test runner with optional future integration support.
- Modify `scripts/run_validation_suite.sh`: validate package metadata and run OpenCode structural tests.

## Non-Goals

- Do not rewrite existing skill behavior for OpenCode.
- Do not inject a global bootstrap message from the iterative-development plugin. `superpowers` owns bootstrap/tool-mapping behavior, and `iterative-development` should remain a focused skill-pack plugin.
- Do not add runtime dependencies.
- Do not add a marketplace workflow for OpenCode unless OpenCode gains one that differs from git package plugins.

### Task 1: Add OpenCode Package Metadata

**Files:**
- Create: `package.json`

- [ ] **Step 1: Write the package metadata**

Create `package.json` with exactly this content:

```json
{
  "name": "iterative-development",
  "version": "0.1.0",
  "type": "module",
  "main": ".opencode/plugins/iterative-development.js"
}
```

- [ ] **Step 2: Validate JSON syntax**

Run:

```bash
python3 -m json.tool package.json > /dev/null
```

Expected: command exits `0` with no output.

- [ ] **Step 3: Commit**

Run:

```bash
git add package.json
git commit -m "feat: add OpenCode package metadata"
```

Expected: commit succeeds.

### Task 2: Add Minimal OpenCode Plugin

**Files:**
- Create: `.opencode/plugins/iterative-development.js`

- [ ] **Step 1: Write the plugin entrypoint**

Create `.opencode/plugins/iterative-development.js` with exactly this content:

```js
/**
 * iterative-development plugin for OpenCode.
 *
 * Registers the bundled skills directory so OpenCode can discover this skill pack
 * when installed from the git package.
 */

import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export const IterativeDevelopmentPlugin = async () => {
  const iterativeDevelopmentSkillsDir = path.resolve(__dirname, '../../skills');

  return {
    config: async (config) => {
      config.skills = config.skills || {};
      config.skills.paths = config.skills.paths || [];

      if (!config.skills.paths.includes(iterativeDevelopmentSkillsDir)) {
        config.skills.paths.push(iterativeDevelopmentSkillsDir);
      }
    }
  };
};
```

- [ ] **Step 2: Verify JavaScript syntax fails before implementation if using TDD**

If Task 2 Step 1 has not been completed yet, run this first:

```bash
node --check .opencode/plugins/iterative-development.js
```

Expected before the file exists: FAIL with `Cannot find module` or file-not-found output.

- [ ] **Step 3: Verify JavaScript syntax passes after implementation**

Run:

```bash
node --check .opencode/plugins/iterative-development.js
```

Expected: command exits `0` with no output.

- [ ] **Step 4: Commit**

Run:

```bash
git add .opencode/plugins/iterative-development.js
git commit -m "feat: register iterative-development skills in OpenCode"
```

Expected: commit succeeds.

### Task 3: Add OpenCode Structural Tests

**Files:**
- Create: `tests/opencode/setup.sh`
- Create: `tests/opencode/test-plugin-loading.sh`
- Create: `tests/opencode/run-tests.sh`

- [ ] **Step 1: Write the test environment setup**

Create `tests/opencode/setup.sh` with exactly this content:

```bash
#!/usr/bin/env bash
# Setup script for OpenCode plugin tests.
# Creates an isolated test environment with the package layout OpenCode installs.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

export TEST_HOME
TEST_HOME=$(mktemp -d)
export HOME="$TEST_HOME"
export XDG_CONFIG_HOME="$TEST_HOME/.config"
export OPENCODE_CONFIG_DIR="$TEST_HOME/.config/opencode"

ITERATIVE_DEVELOPMENT_DIR="$OPENCODE_CONFIG_DIR/iterative-development"
ITERATIVE_DEVELOPMENT_SKILLS_DIR="$ITERATIVE_DEVELOPMENT_DIR/skills"
ITERATIVE_DEVELOPMENT_PLUGIN_FILE="$ITERATIVE_DEVELOPMENT_DIR/.opencode/plugins/iterative-development.js"

mkdir -p "$ITERATIVE_DEVELOPMENT_DIR"
cp -r "$REPO_ROOT/skills" "$ITERATIVE_DEVELOPMENT_DIR/"

mkdir -p "$(dirname "$ITERATIVE_DEVELOPMENT_PLUGIN_FILE")"
cp "$REPO_ROOT/.opencode/plugins/iterative-development.js" "$ITERATIVE_DEVELOPMENT_PLUGIN_FILE"

mkdir -p "$OPENCODE_CONFIG_DIR/plugins"
ln -sf "$ITERATIVE_DEVELOPMENT_PLUGIN_FILE" "$OPENCODE_CONFIG_DIR/plugins/iterative-development.js"

echo "Setup complete: $TEST_HOME"
echo "OPENCODE_CONFIG_DIR:        $OPENCODE_CONFIG_DIR"
echo "iterative-development dir:  $ITERATIVE_DEVELOPMENT_DIR"
echo "Skills dir:                 $ITERATIVE_DEVELOPMENT_SKILLS_DIR"
echo "Plugin file:                $ITERATIVE_DEVELOPMENT_PLUGIN_FILE"
echo "Plugin registered at:       $OPENCODE_CONFIG_DIR/plugins/iterative-development.js"

cleanup_test_env() {
    if [ -n "${TEST_HOME:-}" ] && [ -d "$TEST_HOME" ]; then
        rm -rf "$TEST_HOME"
    fi
}

export -f cleanup_test_env
export REPO_ROOT
export ITERATIVE_DEVELOPMENT_DIR
export ITERATIVE_DEVELOPMENT_SKILLS_DIR
export ITERATIVE_DEVELOPMENT_PLUGIN_FILE
```

- [ ] **Step 2: Write the plugin loading test**

Create `tests/opencode/test-plugin-loading.sh` with exactly this content:

```bash
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

if [ -f "$(readlink -f "$plugin_link")" ]; then
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
```

- [ ] **Step 3: Write the OpenCode test runner**

Create `tests/opencode/run-tests.sh` with exactly this content:

```bash
#!/usr/bin/env bash
# Main test runner for OpenCode plugin tests.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/../.."

echo "========================================"
echo " OpenCode Plugin Test Suite"
echo "========================================"
echo ""
echo "Repository: $(pwd)"
echo "Test time: $(date)"
echo ""

tests=(
    "test-plugin-loading.sh"
)

passed=0
failed=0

for test in "${tests[@]}"; do
    echo "----------------------------------------"
    echo "Running: $test"
    echo "----------------------------------------"

    test_path="$SCRIPT_DIR/$test"
    if output=$(bash "$test_path" 2>&1); then
        echo "  [PASS]"
        passed=$((passed + 1))
    else
        echo "  [FAIL]"
        echo ""
        echo "  Output:"
        printf '%s\n' "$output" | sed 's/^/    /'
        failed=$((failed + 1))
    fi
    echo ""
done

echo "========================================"
echo " Test Results Summary"
echo "========================================"
echo ""
echo "  Passed: $passed"
echo "  Failed: $failed"
echo ""

if [ "$failed" -gt 0 ]; then
    echo "STATUS: FAILED"
    exit 1
fi

echo "STATUS: PASSED"
```

- [ ] **Step 4: Run test before plugin is present if using TDD**

If Task 2 has not been implemented yet, run:

```bash
bash tests/opencode/run-tests.sh
```

Expected before the plugin exists: FAIL because `.opencode/plugins/iterative-development.js` cannot be copied.

- [ ] **Step 5: Run test after plugin is present**

Run:

```bash
bash tests/opencode/run-tests.sh
```

Expected: `STATUS: PASSED`.

- [ ] **Step 6: Commit**

Run:

```bash
git add tests/opencode
git commit -m "test: add OpenCode plugin structure checks"
```

Expected: commit succeeds.

### Task 4: Wire OpenCode Checks Into the Validation Suite

**Files:**
- Modify: `scripts/run_validation_suite.sh:11-17`
- Modify: `scripts/run_validation_suite.sh:56-57`

- [ ] **Step 1: Update manifest validation section**

Replace the existing lines:

```bash
echo "=== Validating plugin manifest ==="
python3 -c "import json; json.load(open('.claude-plugin/plugin.json'))"
echo "OK: .claude-plugin/plugin.json"
```

with:

```bash
echo "=== Validating plugin manifests ==="
python3 -c "import json; json.load(open('.claude-plugin/plugin.json'))"
echo "OK: .claude-plugin/plugin.json"
python3 -c "import json; data=json.load(open('package.json')); assert data['main'] == '.opencode/plugins/iterative-development.js'; assert data['type'] == 'module'"
echo "OK: package.json"
```

- [ ] **Step 2: Add OpenCode checks before final success**

Insert this block before the final `echo "=== All validation checks passed ==="` section:

```bash
echo ""
echo "=== Running OpenCode plugin checks ==="
bash tests/opencode/run-tests.sh
```

- [ ] **Step 3: Run the full validation suite**

Run:

```bash
./scripts/run_validation_suite.sh
```

Expected: all existing Python tests pass, manifest validation prints `OK: package.json`, OpenCode plugin checks print `STATUS: PASSED`, and final output includes `=== All validation checks passed ===`.

- [ ] **Step 4: Commit**

Run:

```bash
git add scripts/run_validation_suite.sh
git commit -m "test: validate OpenCode plugin support"
```

Expected: commit succeeds.

### Task 5: Add OpenCode Installation Docs

**Files:**
- Create: `.opencode/INSTALL.md`
- Create: `docs/README.opencode.md`
- Modify: `README.md:1-4`
- Modify: `README.md:39-49`
- Modify: `README.md:58-60`

- [ ] **Step 1: Write the quick install guide**

Create `.opencode/INSTALL.md` with exactly this content:

```markdown
# Installing iterative-development for OpenCode

## Prerequisites

- [OpenCode.ai](https://opencode.ai) installed
- The [superpowers](https://github.com/obra/superpowers) OpenCode plugin installed for the intended workflow

## Installation

Add both plugins to the `plugin` array in your `opencode.json` global or project config:

```json
{
  "plugin": [
    "superpowers@git+https://github.com/obra/superpowers.git",
    "iterative-development@git+https://github.com/prime-radiant-inc/iterative-development.git"
  ]
}
```

Restart OpenCode. The plugin registers all iterative-development skills automatically.

Verify by using OpenCode's native `skill` tool to list skills, then load `iterative-development/iterative-development`.

## Usage

Use OpenCode's native `skill` tool:

```
use skill tool to list skills
use skill tool to load iterative-development/iterative-development
```

## Updating

OpenCode reinstalls git plugins when it refreshes plugin dependencies. Restart OpenCode after changing plugin config.

To pin a specific version:

```json
{
  "plugin": ["iterative-development@git+https://github.com/prime-radiant-inc/iterative-development.git#v0.1.0"]
}
```

## Troubleshooting

### Plugin not loading

1. Check logs: `opencode run --print-logs "hello" 2>&1 | grep -i iterative`
2. Verify the plugin line in your `opencode.json`
3. Make sure you're running a recent version of OpenCode

### Skills not found

1. Use OpenCode's `skill` tool to list discovered skills
2. Check that the plugin is loading
3. Verify the package has `.opencode/plugins/iterative-development.js` and `skills/*/SKILL.md`

## Getting Help

- Report issues: https://github.com/prime-radiant-inc/iterative-development/issues
- Full documentation: https://github.com/prime-radiant-inc/iterative-development/blob/main/docs/README.opencode.md
```

- [ ] **Step 2: Write the full OpenCode guide**

Create `docs/README.opencode.md` with exactly this content:

```markdown
# iterative-development for OpenCode

Complete guide for using iterative-development with [OpenCode.ai](https://opencode.ai).

## Installation

Add iterative-development and superpowers to the `plugin` array in your `opencode.json` global or project config:

```json
{
  "plugin": [
    "superpowers@git+https://github.com/obra/superpowers.git",
    "iterative-development@git+https://github.com/prime-radiant-inc/iterative-development.git"
  ]
}
```

Restart OpenCode. The iterative-development plugin registers its bundled skills automatically.

## Usage

Use OpenCode's native `skill` tool to list and load skills:

```
use skill tool to list skills
use skill tool to load iterative-development/iterative-development
```

The top-level skill orchestrates the iterative workflow. The supporting skills are also available for direct use:

- `iterative-development/extracting-requirements`
- `iterative-development/scoping-the-simplest-core`
- `iterative-development/running-an-iteration`
- `iterative-development/implementing-tasks`
- `iterative-development/auditing-progress`

## Relationship to superpowers

Install `superpowers` alongside this plugin. `superpowers` provides the general-purpose operating rules, TDD, verification, and OpenCode tool mapping bootstrap. This plugin provides the domain workflow for large-spec iterative development.

## How It Works

The OpenCode plugin does one thing: it registers this package's `skills/` directory through OpenCode's `config` hook. OpenCode then discovers each `SKILL.md` file through its native skill system.

The plugin intentionally does not inject a conversation bootstrap. Bootstrap behavior belongs to `superpowers`; iterative-development should only add its skill pack.

## Updating

OpenCode reinstalls git plugins when it refreshes plugin dependencies. Restart OpenCode after changing plugin config.

To pin a specific version, use a branch or tag:

```json
{
  "plugin": ["iterative-development@git+https://github.com/prime-radiant-inc/iterative-development.git#v0.1.0"]
}
```

## Troubleshooting

### Plugin not loading

1. Check OpenCode logs: `opencode run --print-logs "hello" 2>&1 | grep -i iterative`
2. Verify the plugin line in your `opencode.json`
3. Make sure you're running a recent version of OpenCode

### Skills not found

1. Use OpenCode's `skill` tool to list available skills
2. Check that the plugin is loading
3. Each skill needs a `SKILL.md` file with valid YAML frontmatter

## Development Checks

Run repository validation, including OpenCode structural checks:

```bash
./scripts/run_validation_suite.sh
```

Run only OpenCode structural checks:

```bash
bash tests/opencode/run-tests.sh
```
```

- [ ] **Step 3: Update README description**

Replace the current opening description:

```markdown
A Claude Code plugin that drives an autonomous, audited implementation loop for projects with large, comprehensive, or ambiguous specs. Pairs with [superpowers](https://github.com/obra/superpowers).
```

with:

```markdown
A Claude Code and OpenCode skill pack that drives an autonomous, audited implementation loop for projects with large, comprehensive, or ambiguous specs. Pairs with [superpowers](https://github.com/obra/superpowers).
```

- [ ] **Step 4: Update README installation section**

Replace the existing installation section with:

```markdown
## Installation

### Claude Code

Install from the Prime Radiant marketplace:

```
/plugin marketplace add prime-radiant-inc/prime-radiant-marketplace
/plugin install iterative-development@prime-radiant-marketplace
```

Restart Claude Code after installing.

### OpenCode

Add both plugins to the `plugin` array in your `opencode.json` global or project config:

```json
{
  "plugin": [
    "superpowers@git+https://github.com/obra/superpowers.git",
    "iterative-development@git+https://github.com/prime-radiant-inc/iterative-development.git"
  ]
}
```

Restart OpenCode after installing. See [docs/README.opencode.md](docs/README.opencode.md) for the full OpenCode guide.
```

- [ ] **Step 5: Update relationship section**

Replace the existing relationship paragraph with:

```markdown
This plugin depends conceptually on skills from the `superpowers` plugin (brainstorming, TDD, parallel adversarial review, verification-before-completion). Install `superpowers` alongside `iterative-development` for the intended experience in Claude Code or OpenCode.
```

- [ ] **Step 6: Commit**

Run:

```bash
git add .opencode/INSTALL.md docs/README.opencode.md README.md
git commit -m "docs: add OpenCode installation guide"
```

Expected: commit succeeds.

### Task 6: Final Verification

**Files:**
- Verify: all files changed by Tasks 1-5

- [ ] **Step 1: Run OpenCode structural tests**

Run:

```bash
bash tests/opencode/run-tests.sh
```

Expected: `STATUS: PASSED`.

- [ ] **Step 2: Run full validation suite**

Run:

```bash
./scripts/run_validation_suite.sh
```

Expected: all checks pass and final output includes `=== All validation checks passed ===`.

- [ ] **Step 3: Optional real OpenCode smoke test**

Run this only if `opencode` is installed in the environment:

```bash
opencode run --print-logs "use skill tool to list skills and confirm iterative-development skills are available"
```

Expected: OpenCode can discover the iterative-development skills. If the command cannot run because `opencode` is not installed, record that the integration smoke test was not run and rely on structural tests.

- [ ] **Step 4: Inspect final diff**

Run:

```bash
git diff --stat HEAD~5..HEAD
```

Expected changed areas are limited to `package.json`, `.opencode/`, `docs/README.opencode.md`, `README.md`, `tests/opencode/`, and `scripts/run_validation_suite.sh`.

## Self-Review

- Spec coverage: the plan covers the package entrypoint, plugin registration, install docs, structural tests, and validation-suite integration needed for OpenCode support.
- Placeholder scan: no deferred sections or implementation placeholders remain.
- Type/name consistency: the plugin export, package `main`, symlink path, docs, and tests consistently use `iterative-development` and `.opencode/plugins/iterative-development.js`.
