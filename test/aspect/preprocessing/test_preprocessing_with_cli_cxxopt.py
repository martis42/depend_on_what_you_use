from expected_result import ExpectedResult
from test_case import DwyuImplCompatibility, TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    @property
    def dwyu_impl_compatibility(self) -> DwyuImplCompatibility:
        # The Python based preprocessor does not support all cases we test here
        return DwyuImplCompatibility.CPP_ONLY

    def execute_test_logic(self) -> Result:
        expected = ExpectedResult(success=True)
        actual = self._run_dwyu(
            target="//preprocessing:select_includes_via_external_macros_with_cli_cxxopt",
            extra_args=[
                "--cxxopt=-DTOGGLE",
                "--cxxopt=-DTHE_ANSWER=42",
                '--cxxopt=-DLIB_A_FILE_PATH="support/lib_a.h"',
            ],
            aspect=self.default_aspect,
        )

        return self._check_result(actual=actual, expected=expected)
