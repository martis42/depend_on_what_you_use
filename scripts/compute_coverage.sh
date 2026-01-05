#!/usr/bin/env bash

set -o errexit

# Execute instrumented code and store coverage data
bazel coverage //dwyu/...

# Transform data into html
genhtml  --branch-coverage --output coverage_data "$(bazel info output_path)/_coverage/_coverage_report.dat"

# Display data
firefox coverage_data/index.html
