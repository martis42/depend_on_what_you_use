from expected_result import ExpectedSuccess
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        actual = self._run_dwyu(
            target="//allow_private_headers_from_deps:allow_private_headers_from_deps_via_tag",
            aspect=self.default_aspect,
        )

        return self._check_result(actual=actual, expected=ExpectedSuccess())
