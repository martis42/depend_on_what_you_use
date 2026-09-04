from expected_result import ExpectedSuccess
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        actual = self._run_dwyu(
            # Ensure using transitive and direct deps both work
            target=[
                "//target_mapping:use_lib_a_and_ext_a",
                "//target_mapping:use_lib_a_and_ext_a_privately",
                "//target_mapping:use_lib_b_and_ext_b",
            ],
            aspect=self.choose_aspect("//target_mapping:aspect.bzl%map_transitive_deps_all"),
        )

        return self._check_result(actual=actual, expected=ExpectedSuccess())
