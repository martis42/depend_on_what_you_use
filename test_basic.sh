#!/usr/bin/env bash

set -o errexit
set -o nounset

source ./scripts/print_msg.sh

print_msg "Pre-commit checks"
pre-commit run --all-files

print_msg "Execute unit tests and ensure docs are up to date"
bazel test //...

print_msg "Execute sanitizers"
bazel test --config=sanitize //dwyu/...

print_msg "Execute DWYU"
bazel build --config=dwyu //dwyu/...

print_msg "Execute clang-tidy"
bazel build --config=clang_tidy //dwyu/...

./scripts/ensure_cpp11_compatibility.sh


print_msg "Aspect integration tests scripts unit tests"
./scripts/test_aspect_tests_scripts.sh

print_msg "Build examples"
./scripts/build_examples.sh
