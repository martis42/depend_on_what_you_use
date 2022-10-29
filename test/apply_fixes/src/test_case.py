import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional, Set

from src.result import Result


class TestCaseBase(ABC):
    def __init__(self, name: str) -> None:
        self._name = name
        self._workspace = None
        self._verbose = None

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

    def execute_test(self, workspace: Path, verbose: bool = False) -> Result:
        self._workspace = workspace
        self._verbose = verbose
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
        # Detecting the problems which we want to fix causes a red build, thus don't check results
        if self._verbose:
            subprocess.run(cmd, cwd=self._workspace, check=False)
        else:
            subprocess.run(cmd, cwd=str(self._workspace), stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)

    def _run_automatic_fix(self, extra_args: List[str] = None) -> None:
        """
        Execute the applying fixes script for the Bazel target associated with the test case
        """
        cmd = ["bazel", "run", "@depend_on_what_you_use//:apply_fixes", "--", f"--workspace={self._workspace}"]
        if extra_args:
            cmd.extend(extra_args)
        if self._verbose:
            subprocess.run(cmd, check=True)
        else:
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

    def _get_target_attribute(self, target: str, attribute: str) -> Set["str"]:
        """
        Returns a set to ensure ordering is no issue
        """
        process = subprocess.run(
            ["bazel", "query", f"labels({attribute}, {target})"],
            cwd=self._workspace,
            check=True,
            encoding="utf-8",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if self._verbose:
            print(process.stdout)
        return {dep for dep in process.stdout.split("\n") if dep}
