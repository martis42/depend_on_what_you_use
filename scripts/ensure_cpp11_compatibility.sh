#!/usr/bin/env bash

set -o errexit
set -o nounset

# Due to using warning '-Wc++11-compat' we are confident our own code has C++11 compatibility.
# However, since we ignore warnings from third_party code, we need to make sure that the third_party code is also C++11 compatible.

TARGETS=(
    "//dwyu/aspect/private/preprocessing:main"
    "//dwyu/aspect/private/preprocessing:main_no_preprocessing"
    "//dwyu/aspect/private/process_target:main_cc"
)

echo ""
echo ">> Ensuring the following targets compile with C++11:"
for target in "${TARGETS[@]}"; do
    echo ">>   ${target}"
done
echo ""

bazel build --cxxopt=-std=c++11 --host_cxxopt=-std=c++11 -- ${TARGETS[@]}
