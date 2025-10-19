from expected_result import ExpectedResult
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        expected = ExpectedResult(success=False, unused_public_deps=["//rule_using_aspect:c"])
        actual = self._run_bazel_build(
            target=self.choose_target("//rule_using_aspect:dwyu_recursive_with_impl_deps"),
            extra_args=["--experimental_cc_implementation_deps"],
        )

        return self._check_result(actual=actual, expected=expected)
