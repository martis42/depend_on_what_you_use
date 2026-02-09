from __future__ import annotations

import logging
import shlex
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path

from test.support.result import Error, Result

log = logging.getLogger()


class TestCaseBase(ABC):
    def __init__(self, name: str, test_dir: Path, bazel_binary: Path) -> None:
        self._name = name
        self._test_dir = test_dir
        self._bazel_bin = str(bazel_binary)

    #
    # Interface
    #

    @property
    @abstractmethod
    def test_target(self) -> str:
        """
        Bazel target from workspace under test used in test case implementation
        """

    @abstractmethod
    def execute_test_logic(self) -> Result:
        """
        Overwrite this to implement a concrete test case
        """

    @property
    def windows_compatible(self) -> bool:
        """
        Some test cases are not compatible to a Windows environment
        """
        return True

    #
    # Base Implementation
    #

    @property
    def name(self) -> str:
        return self._name

    @property
    def test_dir(self) -> Path:
        return self._test_dir

    def execute_test(self, log_file: Path) -> Result:
        self._log_file = log_file
        return self.execute_test_logic()

    def _make_create_reports_cmd(
        self,
        aspect: str,
        startup_args: list[str] | None = None,
        extra_args: list[str] | None = None,
    ) -> list[str]:
        cmd_startup_args = startup_args if startup_args else []
        cmd_extra_args = extra_args if extra_args else []
        return [
            self._bazel_bin,
            *cmd_startup_args,
            "build",
            f"--aspects={aspect}",
            "--output_groups=dwyu",
            *cmd_extra_args,
            "--",
            self.test_target,
        ]

    def _create_reports(
        self, aspect: str, startup_args: list[str] | None = None, extra_args: list[str] | None = None
    ) -> None:
        """
        Create report files as input for the applying fixes script.
        Multiple tests are reusing the same workspace. Thus, searching in bazel-out for the DWYU reports would yield
        reports unrelated to the specific test currently running. Therefore, we capture the output of the DWYU command
        into a log file so the applying fixes script can use it as input without being bothered by the DWYU results of
        other tests.
        """
        cmd = self._make_create_reports_cmd(aspect=aspect, startup_args=startup_args, extra_args=extra_args)
        process = self._run_and_capture_cmd(cmd, check=False)
        self._log_file.write_text(process.stdout)

    def _run_automatic_fix(
        self, extra_args: list[str] | None = None, custom_dwyu_report_discovery: bool = False
    ) -> None:
        """
        Execute the applying fixes script for the Bazel target associated with the test case
        """
        verbosity = ["--verbose"] if log.isEnabledFor(logging.DEBUG) else []
        cmd_extra_args = extra_args if extra_args else []
        dwyu_report = [] if custom_dwyu_report_discovery else [f"--dwyu-log-file={self._log_file}", "--use-bazel-info"]

        self._run_cmd(
            cmd=[
                self._bazel_bin,
                "run",
                "@depend_on_what_you_use//:apply_fixes",
                "--",
                *dwyu_report,
                *verbosity,
                *cmd_extra_args,
            ],
            check=True,
        )

    def _get_target_deps(self, target: str) -> set[str]:
        deps = self._get_target_attribute(target=target, attribute="deps")
        # cc_binary and cc_test rules automatically depend on this, but it is irrelevant for our analysis
        # Since, this is added in macro scope to the deps list, query options like '--noimplicit_deps' do not work
        return deps - {"@rules_cc//:link_extra_lib"}

    def _get_target_impl_deps(self, target: str) -> set[str]:
        return self._get_target_attribute(target=target, attribute="implementation_deps")

    def _get_target_attribute(self, target: str, attribute: str) -> set[str]:
        """
        Returns a set to ensure ordering is no issue
        """
        process = self._run_and_capture_cmd(
            cmd=[self._bazel_bin, "query", f"labels({attribute}, {target})"], check=True
        )
        return {dep for dep in process.stdout.split("\n") if dep}

    def _run_cmd(self, cmd: list[str], **kwargs) -> None:
        log.debug(f"Executing command: {shlex.join(cmd)}")
        check = kwargs.pop("check", True)
        if log.isEnabledFor(logging.DEBUG):
            subprocess.run(cmd, check=check, **kwargs)
        else:
            subprocess.run(cmd, capture_output=True, check=check, **kwargs)

    def _run_and_capture_cmd(self, cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
        log.debug(f"Executing command: {shlex.join(cmd)}")
        check = kwargs.pop("check", True)
        process = subprocess.run(cmd, capture_output=True, text=True, check=check, **kwargs)
        log.debug("===== stdout =====")
        log.debug(process.stdout)
        log.debug("----- stderr -----")
        log.debug(process.stderr)
        log.debug("==================")
        return process

    @staticmethod
    def _make_unexpected_output_error(expected: str, output: str) -> Error:
        border = 42 * "-"
        return Error(
            f"Did not find expected output: \n{border}\n{expected}\n{border}\nUnexpected output:\n{border}\n{output}\n{border}\n"
        )

    @staticmethod
    def _make_unexpected_deps_error(
        expected_deps: set[str] | None = None,
        expected_implementation_deps: set[str] | None = None,
        actual_deps: set[str] | None = None,
        actual_implementation_deps: set[str] | None = None,
    ) -> Error:
        message = "Unexpected dependencies.\n"
        if expected_deps:
            message += f"Expected deps: {expected_deps}\n"
            message += f"Actual deps: {actual_deps}\n"
        if expected_implementation_deps:
            message += f"Expected implementation_deps: {expected_implementation_deps}\n"
            message += f"Actual implementation_deps: {actual_implementation_deps}\n"
        return Error(message)
