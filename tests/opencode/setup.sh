#!/usr/bin/env bash
# Setup script for OpenCode plugin tests.
# Creates an isolated test environment with the package layout OpenCode installs.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

export TEST_HOME
TEST_HOME=$(mktemp -d)
TEST_HOME="$(cd "$TEST_HOME" && pwd -P)"
export HOME="$TEST_HOME"
export XDG_CONFIG_HOME="$TEST_HOME/.config"
export OPENCODE_CONFIG_DIR="$TEST_HOME/.config/opencode"

ITERATIVE_DEVELOPMENT_DIR="$OPENCODE_CONFIG_DIR/iterative-development"
ITERATIVE_DEVELOPMENT_SKILLS_DIR="$ITERATIVE_DEVELOPMENT_DIR/skills"
ITERATIVE_DEVELOPMENT_PLUGIN_FILE="$ITERATIVE_DEVELOPMENT_DIR/.opencode/plugins/iterative-development.js"

mkdir -p "$ITERATIVE_DEVELOPMENT_DIR"
cp -r "$REPO_ROOT/skills" "$ITERATIVE_DEVELOPMENT_DIR/"
cp "$REPO_ROOT/package.json" "$ITERATIVE_DEVELOPMENT_DIR/package.json"

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
