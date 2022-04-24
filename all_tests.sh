#!/usr/bin/env bash

set -o errexit
set -o nounset

echo ""
echo "Execute unit tests"
echo
bazel test "//src/..." "//test/aspect:all"

echo ""
echo "Execute acceptance tests - Aspect"
echo ""
./test/aspect/execute_tests.py

echo ""
echo "Execute acceptance tests - Applying fixes"
echo ""
./test/apply_fixes/execute_tests.py
