import logging
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional, Set

from src.result import Result


class TestCaseBase(ABC):
    def __init__(self, name: str) -> None:
        self._name = name
        self._workspace = None

    #
    # Interface
    #

    @property
    @abstractmethod
    def test_target(self) -> str:
        """
        Bazel target used in test case implementation
        """
        pass

    @abstractmethod
    def execute_test_logic(self) -> Result:
        """
        Overwrite this to implement a concrete test case
        """
        pass

    #
    # Base Implementation
    #

    @property
    def name(self) -> str:
        return self._name

    def execute_test(self, workspace: Path) -> Result:
        self._workspace = workspace
        return self.execute_test_logic()

    def _create_reports(self, startup_args: Optional[List[str]] = None, extra_args: Optional[List[str]] = None) -> None:
        """
        Create report files as input for the applying fixes script
        """
        cmd = ["bazel"]
        if startup_args:
            cmd.extend(startup_args)
        cmd.extend(["build", "--aspects=//:aspect.bzl%dwyu_default_aspect", "--output_groups=cc_dwyu_output"])
        if extra_args:
            cmd.extend(extra_args)
        cmd.append(self.test_target)
        self._run_cmd(cmd=cmd, check=False)

    def _run_automatic_fix(self, extra_args: List[str] = None) -> None:
        """
        Execute the applying fixes script for the Bazel target associated with the test case
        """
        cmd = ["bazel", "run", "@depend_on_what_you_use//:apply_fixes", "--", f"--workspace={self._workspace}"]
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
            subprocess.run(cmd, cwd=self._workspace, **kwargs, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def _run_and_capture_cmd(self, cmd: List[str], **kwargs) -> subprocess.CompletedProcess:
        logging.debug(f"Executing command: {cmd}")
        process = subprocess.run(
            cmd, cwd=self._workspace, **kwargs, encoding="utf-8", stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        logging.debug(process.stdout)
        return process
