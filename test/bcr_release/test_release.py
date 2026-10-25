#!/usr/bin/env python3

import argparse
import os
import subprocess
import sys
from pathlib import Path

# No benefit for using logging here
# ruff: noqa: T201

MODULE_TEMPLATE_LINE = 'bazel_dep(name = "depend_on_what_you_use")'


def prepare_test(module: Path, version: str) -> None:
    """
    Prepare the test workspace by adapting it to the version to be tested.
    """
    module_content = module.read_text()
    if MODULE_TEMPLATE_LINE not in module_content:
        print(f"Error: The file '{module}' does not contain the expected line '{MODULE_TEMPLATE_LINE}'")
        sys.exit(1)
    module_content = module_content.replace(
        MODULE_TEMPLATE_LINE, f'bazel_dep(name = "depend_on_what_you_use", version = "{version}")'
    )
    module.write_text(module_content)


def execute_test() -> bool:
    """
    Executes the test by running DWYU on some example targets.
    """
    base_cmd = ["bazel", "build", "--config=dwyu", "--"]

    print("\n>>>>>  Expecting - SUCCESS >>>>>>>>\n")
    ok_process = subprocess.run([*base_cmd, "//:ok"], check=False)
    print("\n<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")

    print("\n>>>>>  Expecting - FAILURE >>>>>>>>\n")
    failure_process = subprocess.run([*base_cmd, "//:failure"], check=False)
    print("\n<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n")

    if ok_process.returncode != 0:
        print('ERROR: The "ok" test failed.')
        return False
    if failure_process.returncode == 0:
        print('ERROR: The "failure" test was expected to fail but it succeeded.')
        return False
    return True


def run_release_test(module: Path, version: str) -> bool:
    original_module_content = module.read_bytes()
    try:
        prepare_test(module=module, version=version)
        success = execute_test()
        if success:
            print("SUCCESS\n")
        else:
            print("FAILURE\n")
        return success
    finally:
        module.write_bytes(original_module_content)


if __name__ == "__main__":
    script_dir = Path(__file__).parent
    module_file = script_dir / "MODULE.bazel"

    # Ensure we can invoke the script from various places
    os.chdir(script_dir)

    parser = argparse.ArgumentParser()
    parser.add_argument("--version", help="Version to test. If not provided, it is requested interactively.")
    args = parser.parse_args()

    version = args.version or input("Which version should be tested?:\n")
    success = run_release_test(module=module_file, version=version)

    sys.exit(0 if success else 1)
