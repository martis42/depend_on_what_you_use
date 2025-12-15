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
echo "Execute sanitizers"
echo ""
bazel test --config=sanitize //...

echo ""
echo "Execute DWYU"
echo ""
bazel build --config=dwyu //...

echo ""
echo "Execute clang-tidy"
echo ""
bazel build --config=clang_tidy //...

echo ""
echo "Aspect integration tests scripts unit tests"
echo ""
./scripts/test_aspect_tests_scripts.sh

echo ""
echo "Build examples"
echo ""
./scripts/build_examples.sh

echo ""
echo "Execute mocked CC toolchain tests"
echo ""
./scripts/test_mocked_cc_toolchains.sh
