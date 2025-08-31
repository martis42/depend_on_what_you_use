#!/usr/bin/env bash

set -o errexit

./test_basic.sh

echo ""
echo "Execute integration tests - Examples with bzlmod"
echo ""
./examples/test.py

echo ""
echo "Execute integration tests - Examples with WORKSPACE setup"
echo ""
./examples/test.py --legacy-workspace

echo ""
echo "Execute workspace integration tests"
echo ""
./test/workspace_integration/test.py

echo ""
echo "Execute upstream CC toolchains integration tests"
echo ""
./test/cc_toolchains/upstream/test.py

echo ""
echo "Execute integration tests - Aspect"
echo ""
./test/aspect/execute_tests.py

echo ""
echo "Execute integration tests - Aspect with C++ implementation"
echo ""
# We only test the default versions, as the C++ implementation is supposed to be a function neutral drop in
./test/aspect/execute_tests.py --only-default-version --cpp_impl_based

echo ""
echo "Execute integration tests - Applying fixes"
echo ""
./test/apply_fixes/execute_tests.py
