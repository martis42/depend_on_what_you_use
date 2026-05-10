#!/usr/bin/env bash

set -o errexit -o nounset -o pipefail

# We prefer Python over Bash for scripting
.github/workflows/release_prep.py --tag $1
