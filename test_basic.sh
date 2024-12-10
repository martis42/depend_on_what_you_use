#!/usr/bin/env bash

set -o errexit
set -o nounset

echo ""
echo "Pre-commit checks"
echo ""
pre-commit run --all-files

echo ""
echo "Execute unit tests"
echo ""
bazel test //...

echo ""
echo "Build aspect integration tests"
echo ""
./scripts/build_aspect_tests.sh

echo ""
echo "Build examples"
echo ""
./scripts/build_examples.sh
