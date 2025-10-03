from expected_result import ExpectedResult
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        expected = ExpectedResult(success=True)
        actual = self._run_dwyu(
            target="//ignore_includes:use_ignored_header_and_std_lib",
            aspect=self.choose_aspect("//ignore_includes:aspect.bzl%extra_ignore_include_paths_aspect"),
        )

        return self._check_result(actual=actual, expected=expected)
