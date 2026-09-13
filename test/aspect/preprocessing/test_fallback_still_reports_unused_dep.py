from expected_result import ExpectedDwyuFailure, ExpectedFailure
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        """
        The fallback to lexically scanning a file must not blanket-suppress findings. A genuinely unused dependency
        has to be reported even when the fallback is active for the analyzed source file.
        """
        target = "//preprocessing/fallback:use_with_unused_dep"
        expected = ExpectedFailure(
            ExpectedDwyuFailure(target=target, unused_public_deps=["//preprocessing/fallback:lib_unused"])
        )
        actual = self._run_dwyu(target=target, aspect=self.default_aspect)

        return self._check_result(actual=actual, expected=expected)
