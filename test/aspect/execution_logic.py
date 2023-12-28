import logging
import subprocess
from importlib.machinery import SourceFileLoader
from os import environ
from pathlib import Path
from typing import Dict, List, Optional

from result import Error
from test_case import TestCaseBase
from version import CompatibleVersions, TestedVersions

TEST_CASES_DIR = Path("test/aspect")


def execute_test(test: TestCaseBase, version: TestedVersions, output_base: Path, extra_args: List[str]) -> bool:
    if not test.compatible_bazel_versions.is_compatible_to(version.bazel):
        logging.info(f"--- Skip '{test.name}' due to incompatible Bazel '{version.bazel}'\n")
        return True
    logging.info(f">>> Test '{test.name}' with Bazel {version.bazel} and Python {version.python}")

    succeeded = False
    result = None
    try:
        result = test.execute_test(version=version, output_base=output_base, extra_args=extra_args)
    except Exception:
        logging.exception("Test failed due to exception:")

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


def main(
    tested_versions: List[TestedVersions],
    version_specific_args: Dict[str, CompatibleVersions],
    bazel: Optional[str] = None,
    python: Optional[str] = None,
    requested_tests: Optional[List[str]] = None,
    list_tests: bool = False,
) -> int:
    workspace_path = get_current_workspace()
    tests_search_dir = workspace_path / TEST_CASES_DIR
    test_files = sorted([Path(x) for x in tests_search_dir.glob("*/test_*.py")])

    if list_tests:
        test_names = [file_to_test_name(test) for test in test_files]
        logging.info("Available test cases:")
        logging.info("\n".join(f"- {t}" for t in test_names))
        return 0

    tests = []
    for test in test_files:
        name = file_to_test_name(test)
        if (requested_tests and any(requested in name for requested in requested_tests)) or (not requested_tests):
            module = SourceFileLoader("", str(test.resolve())).load_module()
            tests.append(module.TestCase(name))

    versions = [TestedVersions(bazel=bazel, python=python)] if bazel and python else tested_versions

    failed_tests = []
    output_root = Path(environ["HOME"]) / ".cache" / "bazel" / workspace_path.relative_to("/")
    for version in versions:
        output_base = output_root / f"aspect_integration_tests_bazel_{version.bazel}_python_{version.python}"
        output_base.mkdir(parents=True, exist_ok=True)

        extra_args = [
            arg
            for arg, valid_versions in version_specific_args.items()
            if valid_versions.is_compatible_to(version.bazel)
        ]

        for test in tests:
            if not execute_test(test=test, version=version, output_base=output_base, extra_args=extra_args):
                failed_tests.append(f"'{test.name}' for Bazel {version.bazel} and Python {version.python}")

    logging.info(f'Running tests {"FAILED" if failed_tests else "SUCCEEDED"}')
    if failed_tests:
        logging.info("\nFailed tests:")
        logging.info("\n".join(f"- {failed}" for failed in failed_tests))
        return 1

    return 0
