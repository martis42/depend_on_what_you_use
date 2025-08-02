from expected_result import ExpectedResult
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        expected = ExpectedResult(success=False, invalid_includes=["/foo/lib.h'"], unused_public_deps=["//:ext_lib"])
        actual = self._run_dwyu(
            target=["//cc_toolchain_preprocessor:use_extern_invalid"],
            aspect="//cc_toolchain_preprocessor:aspect.bzl%dwyu",
        )

        return self._check_result(actual=actual, expected=expected)
