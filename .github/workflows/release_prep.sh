#!/usr/bin/env bash

# This script has to remain in the workflow directory due to its location being hard coded in https://github.com/bazel-contrib/.github/blob/master/.github/workflows/release_ruleset.yaml

set -o errexit -o nounset -o pipefail

# We prefer Python over Bash for scripting
python3 "$(dirname "${BASH_SOURCE[0]}")/../scripts/release_prep.py" --tag "$1"
