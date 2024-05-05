#!/usr/bin/env bash

set -o errexit

cd test/aspect
bazel build //...
cd -
