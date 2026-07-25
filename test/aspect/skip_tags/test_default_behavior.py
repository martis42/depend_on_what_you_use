from expected_result import ExpectedSuccess
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        actual = self._run_dwyu(
            target=["//skip_tags:ignored_by_legacy_default_behavior", "//skip_tags:ignored_by_new_tagging_syntax"],
            aspect=self.default_aspect,
        )

        return self._check_result(actual=actual, expected=ExpectedSuccess())
