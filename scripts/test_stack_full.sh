#!/usr/bin/env bash

set -o errexit
set -o nounset

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)

source "$SCRIPT_DIR"/print_msg.sh

"$SCRIPT_DIR"/test_stack_core.sh

print_msg "Execute integration tests - Examples with bzlmod"
"$SCRIPT_DIR"/../examples/test.py

print_msg "Execute integration tests - Examples with WORKSPACE setup"
"$SCRIPT_DIR"/../examples/test.py --legacy-workspace

print_msg "Execute workspace integration tests"
"$SCRIPT_DIR"/../test/workspace_integration/test.py

print_msg "Execute integration tests - Aspect"
"$SCRIPT_DIR"/../test/aspect/execute_tests.py

print_msg "Execute integration tests - Applying fixes"
"$SCRIPT_DIR"/../test/apply_fixes/execute_tests.py
