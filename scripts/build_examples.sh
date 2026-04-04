#!/usr/bin/env bash

set -o errexit
set -o nounset

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)

cd examples
bazel build //...
cd -
