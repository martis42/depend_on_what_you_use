from expected_result import ExpectedSuccess
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        target = "//using_transitive_dep:main"
        actual = self._run_dwyu(
            target=target,
            aspect=self.default_aspect,
            extra_args=["--aspects_parameters=dwyu_analysis_reports_missing_direct_deps=False"],
        )

        return self._check_result(actual=actual, expected=ExpectedSuccess())
