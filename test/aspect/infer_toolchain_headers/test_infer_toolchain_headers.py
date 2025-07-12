from expected_result import ExpectedResult
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        expected = ExpectedResult(success=True)
        actual = self._run_dwyu(
            target="//infer_toolchain_headers:use_toolchain_header",
            aspect="//infer_toolchain_headers:aspect.bzl%dwyu_infer_headers",
        )

        return self._check_result(actual=actual, expected=expected)
