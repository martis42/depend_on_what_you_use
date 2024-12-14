#!/usr/bin/env bash

set -o errexit
set -o nounset

echo ""
echo "Pre-commit checks"
echo ""
pre-commit run --all-files

echo ""
echo "Execute DWYU unit tests"
echo ""
bazel test //...

echo ""
echo "Aspect integration tests scripts unittests"
echo ""
./scripts/test_aspect_tests_scripts.sh

echo ""
echo "Build examples"
echo ""
./scripts/build_examples.sh
