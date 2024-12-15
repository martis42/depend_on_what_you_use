from __future__ import annotations

import logging
import subprocess
import sys
from copy import deepcopy
from importlib.machinery import SourceFileLoader
from os import environ
from pathlib import Path
from typing import TYPE_CHECKING

from result import Error
from version import CompatibleVersions, TestedVersions

if TYPE_CHECKING:
    from test_case import TestCaseBase

# Allow importing common test support code. Relative imports do not work in our case.
WORKSPACE_TEST_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(WORKSPACE_TEST_DIR))

# We need to adjust the import path first before performing this import
# ruff: noqa: E402
from support.bazel import get_bazel_binary


def execute_test(
    test: TestCaseBase, version: TestedVersions, bazel_bin: Path, output_base: Path, extra_args: list[str]
) -> bool:
    if not test.compatible_bazel_versions.is_compatible_to(version.bazel):
        logging.info(f"--- Skip '{test.name}' due to incompatible Bazel '{version.bazel}'\n")
        return True
    logging.info(f">>> Test '{test.name}' with Bazel {version.bazel} and Python {version.python}")

    succeeded = False
    result = None
    try:
        result = test.execute_test(version=version, bazel_bin=bazel_bin, output_base=output_base, extra_args=extra_args)
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
    process = subprocess.run(
        ["bazel", "--max_idle_secs=5", "info", "workspace"], check=True, capture_output=True, text=True
    )
    return Path(process.stdout.strip())


def get_bazel_rolling_version(bazel_bin: Path) -> str:
    run_env = deepcopy(environ)
    run_env["USE_BAZEL_VERSION"] = "rolling"
    process = subprocess.run(
        [bazel_bin, "--version"], env=run_env, shell=False, check=True, capture_output=True, text=True
    )
    return process.stdout.split("bazel")[1].strip()


def set_rolling_bazel_version(versions: list[TestedVersions], bazel_bin: Path) -> list[TestedVersions]:
    for version in versions:
        if version.bazel == "rolling":
            version.bazel = get_bazel_rolling_version(bazel_bin)
    return versions


def file_to_test_name(test_file: Path) -> str:
    return test_file.parent.name + "/" + test_file.stem.replace("test_", "", 1)


def main(
    tested_versions: list[TestedVersions],
    version_specific_args: dict[str, CompatibleVersions],
    bazel: str | None = None,
    python: str | None = None,
    requested_tests: list[str] | None = None,
    list_tests: bool = False,
    only_default_version: bool = False,
) -> int:
    workspace_path = get_current_workspace()
    test_files = sorted([Path(x) for x in workspace_path.glob("*/test_*.py")])

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

    if bazel and python:
        versions = [TestedVersions(bazel=bazel, python=python)]
    elif only_default_version:
        versions = [version for version in tested_versions if version.is_default]
    else:
        versions = tested_versions

    bazel_binary = get_bazel_binary()
    versions = set_rolling_bazel_version(versions=versions, bazel_bin=bazel_binary)

    failed_tests = []
    output_root = Path.home() / ".cache" / "bazel" / "dwyu"
    for version in versions:
        logging.info(f"""
###
### Aspect integration tests based on: Bazel '{version.bazel}' and Python '{version.python}'
###
""")

        output_base = output_root / f"aspect_integration_tests_bazel_{version.bazel}_python_{version.python}"
        output_base.mkdir(parents=True, exist_ok=True)

        extra_args = [
            arg
            for arg, valid_versions in version_specific_args.items()
            if valid_versions.is_compatible_to(version.bazel)
        ]

        failed_tests.extend(
            [
                f"'{test.name}' for Bazel {version.bazel} and Python {version.python}"
                for test in tests
                if not execute_test(
                    test=test, version=version, bazel_bin=bazel_binary, output_base=output_base, extra_args=extra_args
                )
            ]
        )

    logging.info(f'Running tests {"FAILED" if failed_tests else "SUCCEEDED"}')
    if failed_tests:
        logging.info("\nFailed tests:")
        logging.info("\n".join(f"- {failed}" for failed in failed_tests))
        return 1

    return 0
