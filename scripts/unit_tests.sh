#!/usr/bin/env bash

set -o errexit

bazel test -- //src/... //scripts/... //test/aspect:all //third_party/...
