#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from shutil import rmtree

# No benefit for using logging, and we deliberately use '/tmp' which has no risk in this context
# ruff: noqa: T201n
# ruff: noqa: S108

BCR_DATA_TEMPLATE = """{{
    "build_file": null,
    "build_targets": [],
    "compatibility_level": "0",
    "deps": [],
    "module_dot_bazel": "{module_dot_bazel}",
    "name": "depend_on_what_you_use",
    "patch_strip": 0,
    "patches": [],
    "presubmit_yml": "{presubmit_dot_yml}",
    "strip_prefix": "depend_on_what_you_use-{version}",
    "test_module_build_targets": [],
    "test_module_path": null,
    "test_module_test_targets": [],
    "url": "https://github.com/martis42/depend_on_what_you_use/releases/download/{version}/depend_on_what_you_use-{version}.tar.gz",
    "version": "{version}"
}}
"""

BCR_FORK_REPO = "git@github.com:martis42/bazel-central-registry-fork.git"
BCR_FORK_DIR = Path("/tmp/bcr_fork")


def get_dwyu_files() -> tuple[Path, Path]:
    dwyu_dir = Path(
        subprocess.run(["bazel", "info", "workspace"], capture_output=True, text=True, check=True).stdout.strip()
    )
    print(f"Detected DWYU directory: '{dwyu_dir}'")
    module_file = dwyu_dir / "MODULE.bazel"
    presubmit_file = dwyu_dir / ".bcr/presubmit.yml"

    return module_file, presubmit_file


def setup_bcr_fork() -> None:
    print(f"\nSetup BCR fork at '{BCR_FORK_DIR}'\n")
    if BCR_FORK_DIR.exists():
        rmtree(BCR_FORK_DIR)
    subprocess.run(["git", "clone", BCR_FORK_REPO, BCR_FORK_DIR], check=True)


def prepare_bcr_data(version: str) -> Path:
    module, presubmit = get_dwyu_files()

    module_file_with_version = Path("/tmp/dwyu_with_version.MODULE.bazel")
    with module.open(mode="rt", encoding="utf-8") as module_in:
        module_content = module_in.read()
    with module_file_with_version.open(mode="wt", encoding="utf-8") as module_out:
        module_out.write(module_content.replace('version = "0.0.0",', f'version = "{version}",'))

    bcr_data = Path("/tmp/dwyu_bcr_data.json")
    with bcr_data.open(mode="wt", encoding="utf-8") as bcr_data_out:
        bcr_data_out.write(
            BCR_DATA_TEMPLATE.format(
                version=version, module_dot_bazel=module_file_with_version, presubmit_dot_yml=presubmit
            )
        )

    return bcr_data


def add_dwyu_to_bcr_fork(bcr_data: Path, version: str) -> None:
    print(f"\n========= Adding DWYU '{version}' to BCR fork '{BCR_FORK_DIR}' =========\n")

    subprocess.run(["bazel", "run", "//tools:add_module", "--", "--input", bcr_data], cwd=BCR_FORK_DIR, check=True)
    check_process = subprocess.run(
        ["bazel", "run", "//tools:bcr_validation", "--", "--check", f"depend_on_what_you_use@{version}"],
        cwd=BCR_FORK_DIR,
        check=False,
    )

    print("\n================================================================================\n")

    if check_process.returncode in [
        0,  # All good
        42,  # Check is fine, but a BCR maintainer will have to review
    ]:
        print(f"Successfully added DWYU '{version}' to the BCR fork")
    else:
        print(f"Adding DWYU '{version}' to the BCR fork failed. Look into the terminal output above to find the issue.")
        sys.exit(1)


def push_to_upstream(version: str) -> None:
    yn = input(f"\nDo you want to push DWYU '{version}' [y/n]: ")
    if yn != "y":
        print("Aborting")
        sys.exit(0)

    print("\nPushing release to BCR\n")

    branch = f"depend_on_what_you_use@{version}"
    subprocess.run(["git", "checkout", "-B", branch], cwd=BCR_FORK_DIR, check=True)
    subprocess.run(["git", "add", "modules/depend_on_what_you_use/"], cwd=BCR_FORK_DIR, check=True)
    subprocess.run(["git", "commit", "-m", f"depend_on_what_you_use@{version}"], cwd=BCR_FORK_DIR, check=True)
    subprocess.run(["git", "push", "--set-upstream", "origin", branch], cwd=BCR_FORK_DIR, check=True)


def main() -> None:
    version = input("To be released version: ")
    print()

    bcr_data = prepare_bcr_data(version)
    setup_bcr_fork()
    add_dwyu_to_bcr_fork(bcr_data=bcr_data, version=version)
    push_to_upstream(version)


if __name__ == "__main__":
    main()
