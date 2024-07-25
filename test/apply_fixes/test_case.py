from __future__ import annotations

import logging
import shlex
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path

from result import Error, Result


class TestCaseBase(ABC):
    def __init__(self, name: str, test_sources: Path) -> None:
        self._name = name
        self._test_sources = test_sources
        self._workspace = Path()

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
    def extra_workspace_file_content(self) -> str:
        """
        Overwrite this to append extra content to the WORKSPACE file template
        """
        return ""

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
    def test_sources(self) -> Path:
        return self._test_sources

    def execute_test(self, workspace: Path) -> Result:
        self._workspace = workspace
        return self.execute_test_logic()

    def _make_create_reports_cmd(
        self,
        aspect: str = "default_aspect",
        startup_args: list[str] | None = None,
        extra_args: list[str] | None = None,
    ) -> list[str]:
        cmd_startup_args = startup_args if startup_args else []
        cmd_extra_args = extra_args if extra_args else []
        return [
            "bazel",
            *cmd_startup_args,
            "build",
            f"--aspects=//:aspect.bzl%{aspect}",
            "--output_groups=dwyu",
            *cmd_extra_args,
            "--",
            self.test_target,
        ]

    def _create_reports(
        self,
        aspect: str = "default_aspect",
        startup_args: list[str] | None = None,
        extra_args: list[str] | None = None,
    ) -> None:
        """
        Create report files as input for the applying fixes script
        """
        cmd = self._make_create_reports_cmd(aspect=aspect, startup_args=startup_args, extra_args=extra_args)
        self._run_cmd(cmd=cmd, check=False)

    def _run_automatic_fix(self, extra_args: list[str] | None = None) -> None:
        """
        Execute the applying fixes script for the Bazel target associated with the test case
        """
        verbosity = ["--verbose"] if logging.getLogger().isEnabledFor(logging.DEBUG) else []
        cmd_extra_args = extra_args if extra_args else []

        self._run_cmd(
            cmd=[
                "bazel",
                "run",
                "@depend_on_what_you_use//:apply_fixes",
                "--",
                f"--workspace={self._workspace}",
                *verbosity,
                *cmd_extra_args,
            ],
            check=True,
        )

    def _get_target_attribute(self, target: str, attribute: str) -> set[str]:
        """
        Returns a set to ensure ordering is no issue
        """
        process = self._run_and_capture_cmd(cmd=["bazel", "query", f"labels({attribute}, {target})"], check=True)
        return {dep for dep in process.stdout.split("\n") if dep}

    def _run_cmd(self, cmd: list[str], **kwargs) -> None:
        logging.debug(f"Executing command: {shlex.join(cmd)}")
        check = kwargs.pop("check", True)
        if logging.getLogger().isEnabledFor(logging.DEBUG):
            subprocess.run(cmd, cwd=self._workspace, check=check, **kwargs)
        else:
            subprocess.run(cmd, cwd=self._workspace, capture_output=True, check=check, **kwargs)

    def _run_and_capture_cmd(self, cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
        logging.debug(f"Executing command: {shlex.join(cmd)}")
        check = kwargs.pop("check", True)
        process = subprocess.run(cmd, cwd=self._workspace, capture_output=True, text=True, check=check, **kwargs)
        logging.debug("===== stdout =====")
        logging.debug(process.stdout)
        logging.debug("----- stderr -----")
        logging.debug(process.stderr)
        logging.debug("==================")
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
