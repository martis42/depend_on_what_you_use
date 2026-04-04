#!/usr/bin/env bash

set -o errexit
set -o nounset

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)

cd "$SCRIPT_DIR"/../test/aspect
bazel test //:all
cd -
