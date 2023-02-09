import logging
import subprocess
from distutils.dir_util import copy_tree
from importlib.machinery import SourceFileLoader
from pathlib import Path
from shutil import rmtree
from tempfile import TemporaryDirectory
from typing import List, Optional

from src.test_case import TestCaseBase

TEST_CASES_DIR = Path("test/apply_fixes")
WORKSPACE_TEMPLATE_DIR = TEST_CASES_DIR / "workspace_template"

WORKSPACE_FILE_TEMPLATE = """
local_repository(
    name = "depend_on_what_you_use",
    path = "{dwyu_path}",
)

load("@depend_on_what_you_use//:dependencies.bzl", dwyu_dependencies = "public_dependencies")

dwyu_dependencies()

load("@depend_on_what_you_use//:extra_deps.bzl", "dwyu_extra_deps")

dwyu_extra_deps()
"""


def setup_test_workspace(origin_workspace: Path, test_workspace: Path) -> None:
    test_sources = origin_workspace / WORKSPACE_TEMPLATE_DIR
    copy_tree(src=test_sources, dst=str(test_workspace))
    with open(test_workspace / "WORKSPACE", mode="wt", encoding="utf-8") as ws_file:
        ws_file.write(WORKSPACE_FILE_TEMPLATE.format(dwyu_path=origin_workspace))


def cleanup(test_workspace: Path) -> None:
    """
    Executing a test leaves several traces on the system. For each temporary test workspace an own Bazel server is
    started and a dedicated output base is created. The Bazel server runs for quite some time before timing out, thus
    these servers can block a lot of RAM if the tests are run multiple times.

    This function stops the Bazel server and removes the output directory to prevent test runs from cluttering the host
    system.
    """
    process = subprocess.run(
        ["bazel", "info", "output_base"],
        cwd=test_workspace,
        check=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    output_base = process.stdout.strip()

    subprocess.run(["bazel", "shutdown"], cwd=test_workspace, check=True)

    # Has to be done after the shutdown, otherwise the shutdown will create the output base anew
    rmtree(output_base)


def execute_test(test: TestCaseBase, origin_workspace: Path) -> bool:
    logging.info(f">>> Executing '{test.name}'")
    succeeded = False
    result = None

    with TemporaryDirectory() as test_workspace:
        try:
            setup_test_workspace(origin_workspace=origin_workspace, test_workspace=Path(test_workspace))
            result = test.execute_test(Path(test_workspace))
        except Exception:
            logging.exception("Test failed due to exception:")

        cleanup(test_workspace)

    if result is not None:
        if not result.is_success():
            logging.info(result.error)
        else:
            succeeded = True

    logging.info(f'<<< {"OK" if succeeded else "FAILURE"}\n')

    return succeeded


def get_current_workspace() -> Path:
    process = subprocess.run(
        ["bazel", "info", "workspace"], check=True, encoding="utf-8", stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    return Path(process.stdout.strip())


def file_to_test_name(test_file: Path) -> str:
    return test_file.stem.replace("test_", "", 1)


def main(requested_tests: Optional[List[str]] = None, list_tests: bool = False) -> int:
    current_workspace = get_current_workspace()
    tests_search_dir = current_workspace / TEST_CASES_DIR
    test_files = [Path(x) for x in tests_search_dir.glob("test_*.py")]

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
            tests.append(module.TestCase(name))

    failed_tests = []
    for test in tests:
        succeeded = execute_test(test=test, origin_workspace=current_workspace)
        if not succeeded:
            failed_tests.append(test.name)

    logging.info(f'Running tests {"FAILED" if failed_tests else "SUCCEEDED"}')
    if failed_tests:
        logging.info("\nFailed tests:")
        logging.info("\n".join(f"- '{test}'" for test in failed_tests))
        return 1

    return 0
