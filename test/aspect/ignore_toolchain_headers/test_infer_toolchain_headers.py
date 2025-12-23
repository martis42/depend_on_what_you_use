from expected_result import ExpectedResult
from test_case import DwyuImplCompatibility, TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    """
    This is just a minimal test to ensure we run the toolchain header ignoring with all the incompatible flags
    triggered by the aspect integration tests. More detailed tests for discovering and ignoring toolchain headers are
    done in the integration tests specific to this feature.
    """

    @property
    def dwyu_impl_compatibility(self) -> DwyuImplCompatibility:
        # Toolchain headers are no longer relevant with the C++ based implementation due to being ignored while
        #  preprocessing the code
        return DwyuImplCompatibility.LEGACY_ONLY

    def execute_test_logic(self) -> Result:
        expected = ExpectedResult(success=True)
        actual = self._run_dwyu(
            target="//ignore_toolchain_headers:use_toolchain_header",
            aspect=self.choose_aspect("//ignore_toolchain_headers:aspect.bzl%dwyu_ignore_toolchain_headers"),
        )

        return self._check_result(actual=actual, expected=expected)
