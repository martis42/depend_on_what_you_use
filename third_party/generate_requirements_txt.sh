#! /bin/bash
# This script is used to generates requirements.txt lock file for DWYU used in other projects
set -euo pipefail

CURR_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"

TEMP_DIR="$(mktemp -d)"
trap 'rm -rf "${TEMP_DIR}"' EXIT

function generate_requirements_lock_txt() {
    python3 -m venv "${TEMP_DIR}"
    source "${TEMP_DIR}/bin/activate"

    python3 -m pip install -r "${CURR_DIR}/requirements.in"

    echo "# Auto-generated, DON'T edit!" > "${CURR_DIR}/requirements.txt"
    python3 -m pip freeze >> "${CURR_DIR}/requirements.txt"

    deactivate
}

generate_requirements_lock_txt
