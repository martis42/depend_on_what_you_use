#!/usr/bin/env bash

set -o errexit

bazel build --config=mypy -- //src/... //scripts/... //examples:all //test/aspect:all //test/apply_fixes:all
