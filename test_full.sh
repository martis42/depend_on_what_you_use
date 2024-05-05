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
echo "Execute integration tests - Aspect"
echo ""
./test/aspect/execute_tests.py

echo ""
echo "Execute integration tests - Applying fixes"
echo ""
./test/apply_fixes/execute_tests.py
