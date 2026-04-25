from expected_result import ExpectedSuccess
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        actual = self._run_dwyu(
            target="//skip_toolchain_features:all",
            aspect="//skip_toolchain_features:aspect.bzl%dwyu_skip_toolchain_features",
        )

        return self._check_result(actual=actual, expected=ExpectedSuccess())
