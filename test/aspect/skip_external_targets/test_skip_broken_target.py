from expected_result import ExpectedResult
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        # If we would not skip al external targets the analysis would find an issue with the broken dependency
        expected = ExpectedResult(success=True)
        actual = self._run_dwyu(
            target="@skip_external_deps_test_repo//:broken_dep",
            aspect="//skip_external_targets:aspect.bzl%dwyu_skip_external",
        )

        return self._check_result(actual=actual, expected=expected)
