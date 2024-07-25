#!/usr/bin/env bash

set -o errexit
set -o nounset

echo ""
echo "Pre-commit checks"
echo ""
poetry run pre-commit run --all-files

echo ""
echo "Execute unit tests"
echo ""
./scripts/unit_tests.sh

echo ""
echo "Build aspect integration tests"
echo ""
./scripts/build_aspect_tests.sh

echo ""
echo "Build examples"
echo ""
./scripts/build_examples.sh
