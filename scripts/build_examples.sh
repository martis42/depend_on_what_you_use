#!/usr/bin/env bash

set -o errexit

cd examples
bazel build //...
cd -
