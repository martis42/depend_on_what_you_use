from expected_result import ExpectedDwyuFailure, ExpectedFailure
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        expected = ExpectedFailure(
            ExpectedDwyuFailure(target="//rule_using_aspect:b", unused_public_deps=["//rule_using_aspect:c"])
        )
        actual = self._run_bazel_build(target=self.choose_target("//rule_using_aspect:dwyu_recursive_main"))

        return self._check_result(actual=actual, expected=expected)
