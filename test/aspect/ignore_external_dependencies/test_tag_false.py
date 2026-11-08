from expected_result import ExpectedDwyuFailure, ExpectedFailure
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        target = "//ignore_external_dependencies:use_transitive_external_header_fails_due_to_disabling_by_tag"
        actual = self._run_dwyu(
            target=target, aspect=self.choose_aspect("//ignore_external_dependencies:aspect.bzl%ignore_external")
        )
        expected = ExpectedFailure(
            ExpectedDwyuFailure(
                target=target,
                invalid_includes={"ignore_external_dependencies/use_transitive_external_header.cpp": ["foo.h"]},
            )
        )

        return self._check_result(actual=actual, expected=expected)
