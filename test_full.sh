#!/usr/bin/env bash

set -o errexit
set -o nounset

source ./scripts/print_msg.sh

./test_basic.sh

print_msg "Execute integration tests - Examples with bzlmod"
./examples/test.py

print_msg "Execute integration tests - Examples with WORKSPACE setup"
./examples/test.py --legacy-workspace

print_msg "Execute workspace integration tests"
./test/workspace_integration/test.py

print_msg "Execute integration tests - Aspect"
./test/aspect/execute_tests.py

print_msg "Execute integration tests - Aspect with legacy Python implementation"
# We only test the default versions, as the C++ implementation is supposed to be a function neutral drop in
./test/aspect/execute_tests.py --only-default-version --py_impl_based

print_msg "Execute integration tests - Applying fixes"
./test/apply_fixes/execute_tests.py
