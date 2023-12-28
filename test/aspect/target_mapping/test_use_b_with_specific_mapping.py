from result import ExpectedResult, Result
from test_case import TestCaseBase


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        expected = ExpectedResult(success=True)
        actual = self._run_dwyu(
            target="//test/aspect/target_mapping:use_lib_b",
            aspect="//test/aspect/target_mapping:aspect.bzl%map_specific_deps",
        )

        return self._check_result(actual=actual, expected=expected)
