import logging
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional, Set

from result import Error, Result


class TestCaseBase(ABC):
    def __init__(self, name: str, test_sources: Path) -> None:
        self._name = name
        self._test_sources = test_sources
        self._workspace = None

    #
    # Interface
    #

    @property
    @abstractmethod
    def test_target(self) -> str:
        """
        Bazel target from workspace under test used in test case implementation
        """
        pass

    @abstractmethod
    def execute_test_logic(self) -> Result:
        """
        Overwrite this to implement a concrete test case
        """
        pass

    @property
    def extra_workspace_file_content(self) -> str:
        """
        Overwrite this to append extra content to the WORKSPACE file template
        """
        return ""

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

    def _create_reports(
        self,
        aspect: str = "default_aspect",
        startup_args: Optional[List[str]] = None,
        extra_args: Optional[List[str]] = None,
    ) -> None:
        """
        Create report files as input for the applying fixes script
        """
        cmd = ["bazel"]
        if startup_args:
            cmd.extend(startup_args)
        cmd.extend(["build", f"--aspects=//:aspect.bzl%{aspect}", "--output_groups=cc_dwyu_output"])
        if extra_args:
            cmd.extend(extra_args)
        cmd.append(self.test_target)
        self._run_cmd(cmd=cmd, check=False)

    def _run_automatic_fix(self, extra_args: List[str] = None) -> None:
        """
        Execute the applying fixes script for the Bazel target associated with the test case
        """
        cmd = ["bazel", "run", "@depend_on_what_you_use//:apply_fixes", "--", f"--workspace={self._workspace}"]
        if logging.getLogger().isEnabledFor(logging.DEBUG):
            cmd.append("--verbose")
        if extra_args:
            cmd.extend(extra_args)
        self._run_cmd(cmd=cmd, check=True)

    def _get_target_attribute(self, target: str, attribute: str) -> Set["str"]:
        """
        Returns a set to ensure ordering is no issue
        """
        process = self._run_and_capture_cmd(cmd=["bazel", "query", f"labels({attribute}, {target})"], check=True)
        return {dep for dep in process.stdout.split("\n") if dep}

    def _run_cmd(self, cmd: List[str], **kwargs) -> None:
        logging.debug(f"Executing command: {cmd}")
        if logging.getLogger().isEnabledFor(logging.DEBUG):
            subprocess.run(cmd, cwd=self._workspace, **kwargs)
        else:
            subprocess.run(cmd, cwd=self._workspace, capture_output=True, **kwargs)

    def _run_and_capture_cmd(self, cmd: List[str], **kwargs) -> subprocess.CompletedProcess:
        logging.debug(f"Executing command: {cmd}")
        process = subprocess.run(cmd, cwd=self._workspace, capture_output=True, text=True, **kwargs)
        logging.debug(process.stdout)
        logging.debug(process.stderr)
        return process

    @staticmethod
    def _make_unexpected_output_error(expected: str, output: str) -> Error:
        border = 42 * "-"
        return Error(f"Did not find expected output: {expected}\nUnexpected output:\n{border}\n{output}\n{border}\n")

    @staticmethod
    def _make_unexpected_deps_error(
        expected_deps: Set[str] = None,
        expected_implementation_deps: Set[str] = None,
        actual_deps: Set[str] = None,
        actual_implementation_deps: Set[str] = None,
    ) -> Error:
        message = "Unexpected dependencies.\n"
        if expected_deps:
            message += f"Expected deps: {expected_deps}\n"
            message += f"Actual deps: {actual_deps}\n"
        if expected_implementation_deps:
            message += f"Expected implementation_deps: {expected_implementation_deps}\n"
            message += f"Actual implementation_deps: {actual_implementation_deps}\n"
        return Error(message)
