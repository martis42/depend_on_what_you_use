from expected_result import ExpectedResult
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        expected = ExpectedResult(success=True)
        actual = self._run_dwyu(
            target="//ignore_toolchain_headers:use_custom_toolchain_header",
            aspect=self.choose_aspect("//ignore_toolchain_headers:aspect.bzl%dwyu_custom_toolchain_headers_info"),
        )

        return self._check_result(actual=actual, expected=expected)
