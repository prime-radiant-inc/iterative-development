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
