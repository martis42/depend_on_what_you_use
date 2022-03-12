#!/usr/bin/env bash

set -o errexit
set -o nounset

echo ""
echo "Execute Unit Tests"
echo
bazel test "//src/..." "//test:all"

echo ""
echo "Execute Integration Tests"
echo ""
./test/execute_tests.py
