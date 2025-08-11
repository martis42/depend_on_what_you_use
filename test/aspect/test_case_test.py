from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from test_case import TestCaseBase
from version import TestedVersions

from test.support.result import Error, Result, Success


class TestCaseMock(TestCaseBase):
    def __init__(self, name: str) -> None:
        super().__init__(name, False)
        self.result: Result = Success()
        self.dwyu_extra_args: list[str] = []
        self.target: list[str] | str = "//foo:bar"
        self.bazel_binary = Path("/bazel/binary")

    def execute_test_logic(self) -> Result:
        self._run_dwyu(target=self.target, aspect="//some:aspect", extra_args=self.dwyu_extra_args)
        return self.result


class TestCaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.unit = TestCaseMock("foo")

    @staticmethod
    def get_cmd(mock: MagicMock) -> list[str]:
        """
        We expect only a single call happened.
        A call object is a tuple of (name, positional args, keyword args) and the cmd is the first positional argument.
        """
        return mock.mock_calls[0][1][0]

    @staticmethod
    def get_env(mock: MagicMock) -> dict[str, str]:
        """
        We expect only a single call happened.
        A call object is a tuple of (name, positional args, keyword args) and the env is part of args.
        """
        return mock.mock_calls[0][2]["env"]

    def test_get_name(self) -> None:
        self.assertEqual(self.unit.name, "foo")

    def test_get_default_aspect(self) -> None:
        self.assertEqual(self.unit.default_aspect, "//:aspect.bzl%dwyu")

    @patch("subprocess.run")
    def test_get_success(self, _: MagicMock) -> None:
        result = self.unit.execute_test(
            version=TestedVersions(bazel="6.4.2", python="13.37"),
            bazel_bin=self.unit.bazel_binary,
            output_base=Path("/some/path"),
            extra_args=[],
        )
        self.assertTrue(result.is_success())

    @patch("subprocess.run")
    def test_get_error(self, _: MagicMock) -> None:
        self.unit.result = Error("some failure")
        result = self.unit.execute_test(
            version=TestedVersions(bazel="6.4.2", python="13.37"),
            bazel_bin=self.unit.bazel_binary,
            output_base=Path("/some/path"),
            extra_args=[],
        )
        self.assertFalse(result.is_success())
        self.assertEqual(result.error, "some failure")

    @patch("subprocess.run")
    def test_dwyu_command_without_any_extra_args(self, run_mock: MagicMock) -> None:
        self.unit.execute_test(
            version=TestedVersions(bazel="6.4.2", python="13.37"),
            bazel_bin=self.unit.bazel_binary,
            output_base=Path("/some/path"),
            extra_args=[],
        )

        run_mock.assert_called_once()
        self.assertListEqual(
            self.get_cmd(run_mock),
            [
                "/bazel/binary",
                "--output_base=/some/path",
                "--ignore_all_rc_files",
                "--max_idle_secs=10",
                "build",
                "--experimental_convenience_symlinks=ignore",
                "--noshow_progress",
                "--@rules_python//python/config_settings:python_version=13.37",
                "--aspects=//some:aspect",
                "--output_groups=dwyu",
                "--",
                "//foo:bar",
            ],
        )
        self.assertEqual(self.get_env(run_mock)["USE_BAZEL_VERSION"], "6.4.2")

    @patch("subprocess.run")
    def test_dwyu_command_with_global_and_dwyu_extra_args(self, run_mock: MagicMock) -> None:
        self.unit.dwyu_extra_args = ["--some_arg=42", "--another_arg"]
        self.unit.execute_test(
            version=TestedVersions(bazel="6.4.2", python="13.37"),
            bazel_bin=self.unit.bazel_binary,
            output_base=Path("/some/path"),
            extra_args=["--global_arg=23", "--another_global_arg"],
        )

        run_mock.assert_called_once()
        self.assertListEqual(
            self.get_cmd(run_mock),
            [
                "/bazel/binary",
                "--output_base=/some/path",
                "--ignore_all_rc_files",
                "--max_idle_secs=10",
                "build",
                "--experimental_convenience_symlinks=ignore",
                "--noshow_progress",
                "--global_arg=23",
                "--another_global_arg",
                "--@rules_python//python/config_settings:python_version=13.37",
                "--aspects=//some:aspect",
                "--output_groups=dwyu",
                "--some_arg=42",
                "--another_arg",
                "--",
                "//foo:bar",
            ],
        )
        self.assertEqual(self.get_env(run_mock)["USE_BAZEL_VERSION"], "6.4.2")

    @patch("subprocess.run")
    def test_dwyu_command_with_multiple_targets(self, run_mock: MagicMock) -> None:
        self.unit.target = ["//foo:bar", "//tick:tock"]
        self.unit.execute_test(
            version=TestedVersions(bazel="6.4.2", python="13.37"),
            bazel_bin=self.unit.bazel_binary,
            output_base=Path("/some/path"),
            extra_args=[],
        )

        run_mock.assert_called_once()
        self.assertListEqual(
            self.get_cmd(run_mock),
            [
                "/bazel/binary",
                "--output_base=/some/path",
                "--ignore_all_rc_files",
                "--max_idle_secs=10",
                "build",
                "--experimental_convenience_symlinks=ignore",
                "--noshow_progress",
                "--@rules_python//python/config_settings:python_version=13.37",
                "--aspects=//some:aspect",
                "--output_groups=dwyu",
                "--",
                "//foo:bar",
                "//tick:tock",
            ],
        )
        self.assertEqual(self.get_env(run_mock)["USE_BAZEL_VERSION"], "6.4.2")


if __name__ == "__main__":
    unittest.main()
