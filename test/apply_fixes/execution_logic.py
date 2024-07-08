from __future__ import annotations

import logging
import subprocess
from importlib.machinery import SourceFileLoader
from pathlib import Path, PosixPath
from platform import system
from shutil import copytree, rmtree
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING

from result import Error

if TYPE_CHECKING:
    from test_case import TestCaseBase

TEST_CASES_DIR = Path("test/apply_fixes")
TEST_WORKSPACES_DIR = TEST_CASES_DIR / "workspaces"

MODULE_FILE_TEMPLATE = """
bazel_dep(name = "depend_on_what_you_use")
local_path_override(module_name = "depend_on_what_you_use", path = "{dwyu_path}")

#
# Setup dependencies for test orchestration
#

bazel_dep(name = "bazel_skylib", version = "1.6.1")

bazel_dep(name = "rules_python", version = "0.27.1")
python = use_extension("@rules_python//python/extensions:python.bzl", "python")
python.toolchain(python_version = "3.8")

{extra_content}
"""

BAZEL_RC_FILE = """
# Can improve performance in Windows workers
# See https://github.com/bazelbuild/rules_python/blob/7bba79de34b6352001cb42b801245d0de33ce225/docs/sphinx/pypi-dependencies.md#L40
startup --windows_enable_symlinks

# Decrease Python toolchain overhead
# See https://github.com/bazelbuild/rules_python/issues/1653
common --nolegacy_external_runfiles
common --lockfile_mode=off
"""

BAZEL_VERSION = "7.0.0"


def dwyu_path_as_string(dwyu_path: Path) -> str:
    """
    We can't use the path directly on Windows as we need escaped backslashes
    """
    return str(dwyu_path) if isinstance(dwyu_path, PosixPath) else str(dwyu_path).replace("\\", "\\\\")


def setup_test_workspace(
    origin_workspace: Path, test_sources: Path, extra_workspace_file_content: str, temporary_workspace: Path
) -> None:
    copytree(src=test_sources, dst=str(temporary_workspace), dirs_exist_ok=True)
    with temporary_workspace.joinpath("MODULE.bazel").open(mode="w", encoding="utf-8") as ws_file:
        ws_file.write(
            MODULE_FILE_TEMPLATE.format(
                dwyu_path=dwyu_path_as_string(origin_workspace), extra_content=extra_workspace_file_content
            )
        )
    with temporary_workspace.joinpath(".bazelversion").open(mode="w", encoding="utf-8") as ws_file:
        ws_file.write(BAZEL_VERSION)
    with temporary_workspace.joinpath(".bazelrc").open(mode="w", encoding="utf-8") as ws_file:
        ws_file.write(BAZEL_RC_FILE)


def cleanup(test_workspace: Path) -> None:
    """
    Executing a test leaves several traces on the system. For each temporary test workspace an own Bazel server is
    started and a dedicated output base is created. The Bazel server runs for quite some time before timing out, thus
    these servers can block a lot of RAM if the tests are run multiple times.

    This function stops the Bazel server and removes the output directory to prevent test runs from cluttering the host
    system.
    """
    process = subprocess.run(
        ["bazel", "info", "output_base"], cwd=test_workspace, check=True, capture_output=True, text=True
    )
    output_base = process.stdout.strip()

    # Has to be done before output base cleanup, otherwise the shutdown will create the output base anew
    subprocess.run(["bazel", "shutdown"], cwd=test_workspace, check=True)

    # The hermetic Python toolchain contains read oly files which we can't remove without making them writable
    subprocess.run(["chmod", "-R", "+rw", output_base], check=True)
    rmtree(output_base)


def execute_test(test: TestCaseBase, origin_workspace: Path) -> bool:
    if not test.windows_compatible and system() == "Windows":
        logging.info(f"--- Skipping Test due to Windows incompatibility '{test.name}'")
        return True

    logging.info(f">>> Test '{test.name}'")
    succeeded = False
    result = None

    with TemporaryDirectory() as temporary_workspace:
        workspace_path = Path(temporary_workspace)
        try:
            setup_test_workspace(
                origin_workspace=origin_workspace,
                test_sources=test.test_sources,
                extra_workspace_file_content=test.extra_workspace_file_content,
                temporary_workspace=workspace_path,
            )
            result = test.execute_test(workspace_path)
        except Exception:
            logging.exception("Test failed due to exception:")

        cleanup(workspace_path)

    if result is None:
        result = Error("No result")

    if result.is_success():
        succeeded = True
    else:
        logging.info(result.error)

    logging.info(f'<<< {"OK" if succeeded else "FAILURE"}\n')

    return succeeded


def get_current_workspace() -> Path:
    process = subprocess.run(["bazel", "info", "workspace"], check=True, capture_output=True, text=True)
    return Path(process.stdout.strip())


def file_to_test_name(test_file: Path) -> str:
    return test_file.parent.name + "/" + test_file.stem.replace("test_", "", 1)


def main(requested_tests: list[str] | None = None, list_tests: bool = False) -> int:
    current_workspace = get_current_workspace()
    tests_search_dir = current_workspace / TEST_CASES_DIR
    test_files = [Path(x) for x in tests_search_dir.glob("*/test_*.py")]

    if list_tests:
        test_names = [file_to_test_name(test) for test in test_files]
        logging.info("Available test cases:")
        logging.info("\n".join(f"- {t}" for t in sorted(test_names)))
        return 0

    tests = []
    for test in test_files:
        name = file_to_test_name(test)
        if (requested_tests and any(requested in name for requested in requested_tests)) or (not requested_tests):
            module = SourceFileLoader("", str(test.resolve())).load_module()
            tests.append(module.TestCase(name=name, test_sources=test.parent / "workspace"))

    failed_tests = [test.name for test in tests if not execute_test(test=test, origin_workspace=current_workspace)]
    logging.info(f'Running tests {"FAILED" if failed_tests else "SUCCEEDED"}')
    if failed_tests:
        logging.info("\nFailed tests:")
        logging.info("\n".join(f"- '{test}'" for test in failed_tests))
        return 1

    return 0
