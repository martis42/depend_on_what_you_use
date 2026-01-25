from expected_result import ExpectedDwyuFailure, ExpectedFailure
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        target = "//unused_dep:implementation_deps_lib"
        expected = ExpectedFailure(ExpectedDwyuFailure(target=target, unused_private_deps=["//unused_dep:foo"]))
        actual = self._run_dwyu(target=target, aspect=self.default_aspect)

        return self._check_result(actual=actual, expected=expected)
