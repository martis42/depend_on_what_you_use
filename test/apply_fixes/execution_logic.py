from __future__ import annotations

import logging
import shutil
import subprocess
from dataclasses import dataclass
from importlib.machinery import SourceFileLoader
from pathlib import Path
from platform import system
from tempfile import TemporaryDirectory

from test.apply_fixes.test_case import TestCaseBase
from test.support.bazel import get_bazel_binary, get_current_workspace
from test.support.platform import path_to_starlark_format
from test.support.result import Error

log = logging.getLogger()

MODULE_FILE_TEMPLATE = """
bazel_dep(name = "depend_on_what_you_use")
local_path_override(module_name = "depend_on_what_you_use", path = "{dwyu_path}")

#
# Setup dependencies for test orchestration
#

bazel_dep(name = "bazel_skylib", version = "1.6.1")

# We specify by design an outdated rules_cc version.
# bzlmod resolves dependencies to the maximum of all requested versions for all involved modules.
# Specifying an ancient version here gives us in the end at least whatever rules_cc version DWYU defines as dependency.
bazel_dep(name = "rules_cc", version = "0.0.1")

# We specify by design an outdated rules_python version.
# bzlmod resolves dependencies to the maximum of all requested versions for all involved modules.
# Specifying an ancient version here gives us in the end at least whatever rules_python version DWYU defines as dependency.
bazel_dep(name = "rules_python", version = "0.12.0")
python = use_extension("@rules_python//python/extensions:python.bzl", "python")
python.toolchain(python_version = "3.8")

{extra_content}
"""

BAZEL_RC_FILE = """
# Useless as the workspace are thrown away after each creation
common --lockfile_mode=off

# Some users require this setting to mitigate issues due to a large PYTHONPATH created by rules_python
build --noexperimental_python_import_all_repositories
"""


@dataclass
class TestDefinition:
    name: str
    script: Path
    sources: Path


class ApplyFixesIntegrationTestsExecutor:
    def __init__(self, requested_tests: list[str] | None) -> None:
        self.requested_tests = requested_tests if requested_tests else []

        self.bazel_bin = get_bazel_binary()
        self.origin_workspace = get_current_workspace(self.bazel_bin)
        self.test_definitions = self._get_test_definitions()

    def list_tests(self) -> None:
        log.info("Available test cases:")
        log.info("\n".join(f"- {t.name}" for t in self.test_definitions))

    def execute_tests(self) -> list[str]:
        """
        :return: List of failed test cases
        """
        tests = []
        for test in self.test_definitions:
            if not self.requested_tests or any(requested in test.name for requested in self.requested_tests):
                module = SourceFileLoader("", str(test.script.resolve())).load_module()
                tests.append(module.TestCase(name=test.name, test_sources=test.sources, bazel_binary=self.bazel_bin))

        return [test.name for test in tests if not self._execute_test(test)]

    def _execute_test(self, test: TestCaseBase) -> bool:
        if not test.windows_compatible and system() == "Windows":
            log.info(f"--- Skipping Test due to Windows incompatibility '{test.name}'")
            return True

        log.info(f">>> Test '{test.name}'")
        succeeded = False
        result = None

        with TemporaryDirectory() as temporary_workspace:
            workspace_path = Path(temporary_workspace)
            try:
                self._setup_test_workspace(test=test, test_workspace=workspace_path)
                result = test.execute_test(workspace_path)
            except Exception:
                log.exception("Test failed due to exception:")
            self._cleanup(workspace_path)

        if result is None:
            result = Error("No result")
        if result.is_success():
            succeeded = True
        else:
            log.info(result.error)
        log.info(f"<<< {'OK' if succeeded else 'FAILURE'}\n")

        return succeeded

    def _setup_test_workspace(self, test: TestCaseBase, test_workspace: Path) -> None:
        shutil.copytree(src=test.test_sources, dst=str(test_workspace), dirs_exist_ok=True)
        shutil.copy(self.origin_workspace / ".bazelversion", test_workspace / ".bazelversion")
        (test_workspace / "MODULE.bazel").write_text(
            MODULE_FILE_TEMPLATE.format(
                dwyu_path=path_to_starlark_format(self.origin_workspace),
                extra_content=test.extra_workspace_file_content,
            )
        )
        (test_workspace / ".bazelrc").write_text(BAZEL_RC_FILE)

    def _cleanup(self, test_workspace: Path) -> None:
        """
        Executing a test leaves several traces on the system. For each temporary test workspace an own Bazel server is
        started and a dedicated output base is created. The Bazel server runs for quite some time before timing out, thus
        these servers can block a lot of RAM if the tests are run multiple times.

        This function stops the Bazel server and removes the output directory to prevent test runs from cluttering the host
        system.
        """
        process = subprocess.run(
            [self.bazel_bin, "info", "output_base"], cwd=test_workspace, check=True, capture_output=True, text=True
        )
        output_base = process.stdout.strip()

        # Has to be done before output base cleanup, otherwise the shutdown will create the output base anew
        subprocess.run([self.bazel_bin, "shutdown"], cwd=test_workspace, check=True)

        # The hermetic Python toolchain contains read oly files which we can't remove without making them writable
        subprocess.run(["chmod", "-R", "+rw", output_base], check=True)
        shutil.rmtree(output_base)

    def _get_test_definitions(self) -> list[TestDefinition]:
        tests_search_dir = self.origin_workspace / "test/apply_fixes"
        test_scripts = [Path(file) for file in sorted(tests_search_dir.glob("*/test_*.py"))]
        return [
            TestDefinition(
                name=file.parent.name + "/" + file.stem.replace("test_", "", 1),
                script=file,
                sources=file.parent / "workspace",
            )
            for file in test_scripts
        ]


def main(requested_tests: list[str] | None = None, list_tests: bool = False) -> int:
    executor = ApplyFixesIntegrationTestsExecutor(requested_tests)

    if list_tests:
        executor.list_tests()
        return 0

    failed_tests = executor.execute_tests()
    log.info(f"Running tests {'FAILED' if failed_tests else 'SUCCEEDED'}")
    if failed_tests:
        log.info("\nFailed tests:")
        log.info("\n".join(f"- '{test}'" for test in failed_tests))
        return 1

    return 0
