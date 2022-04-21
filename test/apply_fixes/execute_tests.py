#!/usr/bin/env python3

import subprocess
import sys
import tempfile
from distutils.dir_util import copy_tree
from pathlib import Path

WORKSPACE_TEMPLATE = """
local_repository(
    name = "depend_on_what_you_use",
    path = "{dwyu_repo}",
)

load("@depend_on_what_you_use//:dependencies.bzl", dwyu_public_dependencies = "public_dependencies")

dwyu_public_dependencies()
"""

# TODO generalize impl


def get_current_workspace() -> Path:
    process = subprocess.run(["bazel", "info", "workspace"], check=True, capture_output=True, text=True)
    return Path(process.stdout.strip())


def main():
    success = True
    with tempfile.TemporaryDirectory() as test_workspace:
        try:
            current_workspace = get_current_workspace()
            test_sources = current_workspace / "test/apply_fixes/unused_dependencies"

            # Setup test workspace
            print(f"INFO: Created temporary directory for testing unused dependency removal: '{test_workspace}'")
            copy_tree(src=test_sources, dst=test_workspace)
            with open(Path(test_workspace) / "WORKSPACE", mode="wt", encoding="utf-8") as ws_file:
                ws_file.write(WORKSPACE_TEMPLATE.format(dwyu_repo=current_workspace))

            # create report file for unused dependency by running DWYU
            subprocess.run(
                [
                    "bazel",
                    "build",
                    "//:main",
                    "--aspects=//:aspect.bzl%dwyu_default_aspect",
                    "--output_groups=cc_dwyu_output",
                ],
                cwd=test_workspace,
                check=False,
            )

            # Perform automatic fix
            subprocess.run(
                ["bazel", "run", "@depend_on_what_you_use//:apply_fixes", "--", f"--workspace={test_workspace}"],
                check=True,
            )

            # Make sure the unused dependency has been removed
            process = subprocess.run(
                ["bazel", "query", "labels(deps, //:main)"],
                cwd=test_workspace,
                check=True,
                capture_output=True,
                text=True,
            )
            deps_after_fix = {dep for dep in process.stdout.split("\n") if dep}
            expected_deps = {"//:used"}
            if expected_deps != deps_after_fix:
                success = False
                print(f"FAILED due to unexpected dependencies: {deps_after_fix}")
                print(f"       expected: {expected_deps}")

        # pylint: disable=broad-except
        except Exception as ex:
            success = False
            print(f"FAILED due to excpetion: {ex}")

        # Make sure the bazel cache dir is no swamped with dead test workspaces
        subprocess.run(["bazel", "clean", "--expunge"], check=True)

    if success:
        print("Testing automatic fixes: SUCCESS")
        return 0
    print("Testing automatic fixes: FAILURE")
    return 1


if __name__ == "__main__":
    sys.exit(main())
