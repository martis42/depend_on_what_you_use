import unittest
from pathlib import Path
from typing import Any, List
from unittest.mock import MagicMock, Mock, patch

from result import Error, Result, Success
from test_case import TestCaseBase
from version import TestedVersions


class TestCaseMock(TestCaseBase):
    def __init__(self, name: str):
        super().__init__(name)
        self.result = Success()
        self.dwyu_extra_args: List[str] = []
        self.target = "//foo:bar"

    def execute_test_logic(self) -> Result:
        self._run_dwyu(target=self.target, aspect="//some:aspect", extra_args=self.dwyu_extra_args)
        return self.result


class TestCaseTests(unittest.TestCase):
    def setUp(self):
        self.unit = TestCaseMock("foo")
        self.unit._bazel_binary = Mock(return_value="/bazel/binary")

    @staticmethod
    def get_cmd(mock: MagicMock) -> Any:
        """
        We expect only a single call happened.
        A call object is a tuple of (name, positional args, keyword args) and the cmd is the first positional argument.
        """
        return mock.mock_calls[0][1][0]

    @staticmethod
    def get_env(mock: MagicMock) -> Any:
        """
        We expect only a single call happened.
        A call object is a tuple of (name, positional args, keyword args) and the env is part of args.
        """
        return mock.mock_calls[0][2]["env"]

    def test_get_name(self):
        self.assertEqual(self.unit.name, "foo")

    def test_get_default_aspect(self):
        self.assertEqual(self.unit.default_aspect, "//:aspect.bzl%dwyu")

    @patch("subprocess.run")
    def test_get_success(self, _):
        result = self.unit.execute_test(
            version=TestedVersions(bazel="6.4.2", python="13.37"), output_base=Path("/some/path"), extra_args=[]
        )
        self.assertTrue(result.is_success())

    @patch("subprocess.run")
    def test_get_error(self, _):
        self.unit.result = Error("some failure")
        result = self.unit.execute_test(
            version=TestedVersions(bazel="6.4.2", python="13.37"), output_base=Path("/some/path"), extra_args=[]
        )
        self.assertFalse(result.is_success())
        self.assertEqual(result.error, "some failure")

    @patch("subprocess.run")
    def test_dwyu_command_without_any_extra_args(self, run_mock):
        self.unit.execute_test(
            version=TestedVersions(bazel="6.4.2", python="13.37"), output_base=Path("/some/path"), extra_args=[]
        )

        run_mock.assert_called_once()
        self.assertListEqual(
            self.get_cmd(run_mock),
            [
                "/bazel/binary",
                "--output_base=/some/path",
                "--noworkspace_rc",
                "build",
                "--experimental_convenience_symlinks=ignore",
                "--noshow_progress",
                "--nolegacy_external_runfiles",
                "--@rules_python//python/config_settings:python_version=13.37",
                "--aspects=//some:aspect",
                "--output_groups=dwyu",
                "--",
                "//foo:bar",
            ],
        )
        self.assertEqual(self.get_env(run_mock)["USE_BAZEL_VERSION"], "6.4.2")

    @patch("subprocess.run")
    def test_dwyu_command_with_global_and_dwyu_extra_args(self, run_mock):
        self.unit.dwyu_extra_args = ["--some_arg=42", "--another_arg"]
        self.unit.execute_test(
            version=TestedVersions(bazel="6.4.2", python="13.37"),
            output_base=Path("/some/path"),
            extra_args=["--global_arg=23", "--another_global_arg"],
        )

        run_mock.assert_called_once()
        self.assertListEqual(
            self.get_cmd(run_mock),
            [
                "/bazel/binary",
                "--output_base=/some/path",
                "--noworkspace_rc",
                "build",
                "--experimental_convenience_symlinks=ignore",
                "--noshow_progress",
                "--nolegacy_external_runfiles",
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
    def test_dwyu_command_with_multiple_targets(self, run_mock):
        self.unit.target = ["//foo:bar", "//tick:tock"]
        self.unit.execute_test(
            version=TestedVersions(bazel="6.4.2", python="13.37"), output_base=Path("/some/path"), extra_args=[]
        )

        run_mock.assert_called_once()
        self.assertListEqual(
            self.get_cmd(run_mock),
            [
                "/bazel/binary",
                "--output_base=/some/path",
                "--noworkspace_rc",
                "build",
                "--experimental_convenience_symlinks=ignore",
                "--noshow_progress",
                "--nolegacy_external_runfiles",
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
