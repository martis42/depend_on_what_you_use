#!/usr/bin/env bash

set -o errexit

cd test/cc_toolchains/mocked
bazel test //:all
cd -
