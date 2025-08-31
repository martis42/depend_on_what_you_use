from __future__ import annotations

import logging
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from shlex import join as shlex_join

from expected_result import ExpectedResult
from version import CompatibleVersions, TestedVersions

from test.support.bazel import make_bazel_version_env
from test.support.result import Error, Result, Success

log = logging.getLogger()


class TestCaseBase(ABC):
    def __init__(self, name: str, cpp_impl_based: bool) -> None:
        self._name = name
        self._cpp_impl_based = cpp_impl_based
        self._tested_versions = TestedVersions(bazel="", python="")
        self._output_base: Path | None = None
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
        return self.choose_aspect("//:aspect.bzl%dwyu")

    @property
    def default_aspect_impl_deps(self) -> str:
        return self.choose_aspect("//:aspect.bzl%dwyu_impl_deps")

    def choose_aspect(self, aspect: str) -> str:
        return aspect + "_cpp" if self._cpp_impl_based else aspect

    def execute_test(
        self, version: TestedVersions, bazel_bin: Path, output_base: Path | None, extra_args: list[str]
    ) -> Result:
        self._tested_versions = version
        self._bazel_bin = bazel_bin
        self._output_base = output_base
        self._extra_args = extra_args
        return self.execute_test_logic()

    @staticmethod
    def _check_result(actual: subprocess.CompletedProcess, expected: ExpectedResult) -> Result:
        as_expected = expected.matches_expectation(return_code=actual.returncode, dwyu_output=actual.stdout)

        log_level = logging.DEBUG if as_expected else logging.INFO
        log.log(log_level, "----- DWYU stdout -----")
        log.log(log_level, actual.stdout.strip())
        log.log(log_level, "----- DWYU stderr -----")
        log.log(log_level, actual.stderr.strip())
        log.log(log_level, "-----------------------")

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
        output_base_arg = [f"--output_base={self._output_base}"] if self._output_base else []
        extra_args = extra_args if extra_args else []
        targets = target if isinstance(target, list) else [target]

        test_env = make_bazel_version_env(self._tested_versions.bazel)
        cmd = [
            str(self._bazel_bin),
            *output_base_arg,
            # Testing over many Bazel versions does work well with a static bazelrc file including flags which might not
            # be available in a some tested Bazel version.
            "--ignore_all_rc_files",
            # Do not waste memory by keeping idle Bazel servers around
            "--max_idle_secs=10",
            "build",
            "--experimental_convenience_symlinks=ignore",
            "--noshow_progress",
            *self._extra_args,
            *extra_args,
            "--",
            *targets,
        ]
        log.debug(f"Executing: {shlex_join(cmd)}\n")

        return subprocess.run(cmd, env=test_env, capture_output=True, text=True, check=False)
