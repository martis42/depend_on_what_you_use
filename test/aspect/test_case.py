from __future__ import annotations

import logging
import subprocess
from abc import ABC, abstractmethod
from copy import deepcopy
from os import environ
from pathlib import Path
from shlex import join as shlex_join
from shutil import which

from result import Error, ExpectedResult, Result, Success
from version import CompatibleVersions, TestedVersions


class TestCaseBase(ABC):
    def __init__(self, name: str) -> None:
        self._name = name
        self._tested_versions = TestedVersions(bazel="", python="")
        self._output_base = Path()
        self._extra_args: list[str] = []

    #
    # Interface
    #

    @abstractmethod
    def execute_test_logic(self) -> Result:
        """
        Overwrite this to implement a concrete test case
        """

    @property
    def compatible_bazel_versions(self) -> CompatibleVersions:
        """
        Overwrite this if the test case works only with specific Bazel versions
        """
        return CompatibleVersions()

    #
    # Base Implementation
    #

    @property
    def name(self) -> str:
        return self._name

    @property
    def default_aspect(self) -> str:
        return "//:aspect.bzl%dwyu"

    def execute_test(self, version: TestedVersions, output_base: Path, extra_args: list[str]) -> Result:
        self._tested_versions = version
        self._output_base = output_base
        self._extra_args = extra_args
        return self.execute_test_logic()

    @staticmethod
    def _check_result(actual: subprocess.CompletedProcess, expected: ExpectedResult) -> Result:
        as_expected = expected.matches_expectation(return_code=actual.returncode, dwyu_output=actual.stdout)

        log_level = logging.DEBUG if as_expected else logging.INFO
        logging.log(log_level, "----- DWYU stdout -----")
        logging.log(log_level, actual.stdout.strip())
        logging.log(log_level, "----- DWYU stderr -----")
        logging.log(log_level, actual.stderr.strip())
        logging.log(log_level, "-----------------------")

        return Success() if as_expected else Error("DWYU did not behave as expected")

    def _run_dwyu(
        self, target: str | list[str], aspect: str, extra_args: list[str] | None = None
    ) -> subprocess.CompletedProcess:
        extra_args = extra_args if extra_args else []
        return self._run_bazel_build(
            target=target,
            extra_args=[
                f"--@rules_python//python/config_settings:python_version={self._tested_versions.python}",
                f"--aspects={aspect}",
                "--output_groups=dwyu",
                *extra_args,
            ],
        )

    def _run_bazel_build(
        self, target: str | list[str], extra_args: list[str] | None = None
    ) -> subprocess.CompletedProcess:
        extra_args = extra_args if extra_args else []
        targets = target if isinstance(target, list) else [target]

        test_env = deepcopy(environ)
        test_env["USE_BAZEL_VERSION"] = self._tested_versions.bazel

        cmd = [
            self._bazel_binary(),
            f"--output_base={self._output_base}",
            # Testing over many Bazel versions does work well with a static bazelrc file including flags which might not
            # be available in a some tested Bazel version.
            "--noworkspace_rc",
            "build",
            "--experimental_convenience_symlinks=ignore",
            "--noshow_progress",
            "--nolegacy_external_runfiles",
            *self._extra_args,
            *extra_args,
            "--",
            *targets,
        ]
        logging.debug(f"Executing: {shlex_join(cmd)}\n")

        return subprocess.run(cmd, env=test_env, capture_output=True, text=True, check=False)

    @staticmethod
    def _bazel_binary() -> str:
        bazel = which("bazel") or which("bazelisk")
        if not bazel:
            raise RuntimeError("No bazel or bazelisk binary available on your system")
        return bazel
