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
./scripts/unit_tests.sh

echo ""
echo "Executing mypy"
echo ""
./scripts/mypy.sh

echo ""
echo "Build aspect integration tests"
echo ""
cd test/aspect
bazel build //...
cd -

echo ""
echo "Build examples"
echo ""
cd examples
bazel build //...
cd -

echo ""
echo "Execute integration tests - Aspect"
echo ""
./test/aspect/execute_tests.py

echo ""
echo "Execute integration tests - Applying fixes"
echo ""
./test/apply_fixes/execute_tests.py

echo ""
echo "Execute integration tests - Examples with bzlmod"
echo ""
./examples/test.py

echo ""
echo "Execute integration tests - Examples with WORKSPACE setup"
echo ""
./examples/test.py --legacy-workspace
