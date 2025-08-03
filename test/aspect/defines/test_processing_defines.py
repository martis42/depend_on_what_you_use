from expected_result import ExpectedResult
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    @property
    def test_target(self) -> list[str]:
        target = ["//defines:all"]
        if self._cc_toolchain_based:
            target.append("-//defines:include_using_pre_processor_token")
        else:
            target.append("-//defines:include_using_pre_processor_token_cct")
        return target

    def execute_test_logic(self) -> Result:
        expected = ExpectedResult(success=True)
        actual = self._run_dwyu(target=self.test_target, aspect=self.default_aspect)

        return self._check_result(actual=actual, expected=expected)
