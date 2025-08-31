#!/usr/bin/env bash

# Minimum C++ version which we require for our tools
bazel build --copt="-std=c++11" //dwyu/aspect/private/process_target:main_cc

# Ensure we are not using things which have been deprecated from the C++ standard
bazel build --copt="-std=c++23" //dwyu/aspect/private/process_target:main_cc
