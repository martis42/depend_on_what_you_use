#!/usr/bin/env bash

set -o errexit
set -o nounset

echo ""
echo "Pre-commit checks"
echo ""
poetry run pre-commit run --all-files

echo ""
echo "Execute unit tests"
echo ""
bazel test -- //src/... //test/aspect:all //third_party/...

echo ""
echo "Executing mypy"
echo ""
bazel build --config=mypy -- //src/... //test/aspect:all //test/apply_fixes:all

echo ""
echo "Execute integration tests - Aspect"
echo ""
./test/aspect/execute_tests.py

echo ""
echo "Execute interation tests - Applying fixes"
echo ""
./test/apply_fixes/execute_tests.py

echo ""
echo "Execute interation tests - Examples with bzlmod"
echo ""
cd examples
./test.py

echo ""
echo "Execute interation tests - Examples with WORKSPACE setup"
echo ""
./test.py --legacy-workspace
