from expected_result import ExpectedSuccess
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        actual = self._run_dwyu(
            target="//target_mapping:use_ext_via_with_external_dep",
            aspect=self.choose_aspect("//target_mapping:aspect.bzl%map_direct_deps_filtered"),
        )

        return self._check_result(actual=actual, expected=ExpectedSuccess())
