from expected_result import ExpectedSuccess
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        actual = self._run_dwyu(
            target=[
                "//ignore_external_dependencies:unused_external_deps",
                "//ignore_external_dependencies:use_external_generated_header",
                "//ignore_external_dependencies:use_external_tree_header",
                "//ignore_external_dependencies:use_external_virtual_header",
                "//ignore_external_dependencies:use_transitive_external_header",
            ],
            aspect=self.choose_aspect("//ignore_external_dependencies:aspect.bzl%ignore_external"),
        )
        return self._check_result(actual=actual, expected=ExpectedSuccess())
