#!/usr/bin/env bash

set -o errexit

cd test/aspect
bazel build --enable_bzlmod --aspects=//infer_toolchain_headers:aspect.bzl%dwyu_infer_headers --output_groups=dwyu //infer_toolchain_headers:use_toolchain_header
cd -