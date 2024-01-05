#!/usr/bin/env bash

set -o errexit

bazel test -- //src/... //test/aspect:all //third_party/...
