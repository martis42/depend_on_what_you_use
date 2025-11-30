#!/usr/bin/env bash

TARGETS=("//dwyu/aspect/private/preprocessing:main" "//dwyu/aspect/private/preprocessing:main_no_preprocessing" "//dwyu/aspect/private/process_target:main_cc")
CXXOPTS=("--cxxopt=-pedantic" "--cxxopt=-Wall" "--cxxopt=-Wextra" "--cxxopt=-Werror")

# Minimum C++ version which we require for our tools
bazel build --cxxopt="-std=c++11" ${CXXOPTS[@]} -- ${TARGETS[@]}

# Ensure we are not using things which have been deprecated from the C++ standard
bazel build --cxxopt="-std=c++23" ${CXXOPTS[@]} -- ${TARGETS[@]}
