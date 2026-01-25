from expected_result import ExpectedSuccess
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        # If we would not skip all external targets the analysis would find an issue with the broken dependency
        actual = self._run_dwyu(
            target="@skip_external_deps_test_repo//:broken_dep",
            aspect=self.choose_aspect("//skip_external_targets:aspect.bzl%dwyu_skip_external"),
        )

        return self._check_result(actual=actual, expected=ExpectedSuccess())
