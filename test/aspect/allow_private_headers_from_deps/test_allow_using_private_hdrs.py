from expected_result import ExpectedSuccess
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        actual = self._run_dwyu(
            target="//allow_private_headers_from_deps:use_private_headers_from_deps",
            aspect="//allow_private_headers_from_deps:aspect.bzl%dwyu_with_priv_hdrs",
        )

        return self._check_result(actual=actual, expected=ExpectedSuccess())
