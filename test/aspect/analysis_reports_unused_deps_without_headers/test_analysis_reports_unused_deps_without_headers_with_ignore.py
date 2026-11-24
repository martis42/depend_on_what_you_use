from expected_result import ExpectedSuccess
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        actual = self._run_dwyu(
            target="//analysis_reports_unused_deps_without_headers:main",
            aspect=self.choose_aspect(
                "//analysis_reports_unused_deps_without_headers:aspect.bzl%report_and_ignore",
            ),
        )

        return self._check_result(actual=actual, expected=ExpectedSuccess())
