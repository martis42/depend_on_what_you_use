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
echo "Ensure our C++ code is compliant to the desired C++ versions range and has no warnings"
echo ""
./scripts/test_cpp_version_compliance_and_warnings.sh

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
