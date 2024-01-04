from result import ExpectedResult, Result
from test_case import TestCaseBase


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        expected = ExpectedResult(success=True)
        actual = self._run_dwyu(
            target="//target_mapping:use_lib_b",
            aspect="//target_mapping:aspect.bzl%map_direct_deps",
        )

        return self._check_result(actual=actual, expected=expected)
