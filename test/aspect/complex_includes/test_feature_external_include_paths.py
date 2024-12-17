from expected_result import ExpectedResult
from test_case import CompatibleVersions, TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    @property
    def compatible_bazel_versions(self) -> CompatibleVersions:
        """
        The 'external_include_paths' feature exists for Bazel < 7.0.0. But the corresponding information was not added
        to CompilationContext, which hides it from an aspect. This information was added in Bazel 7.0.0.
        """
        return CompatibleVersions(minimum="7.0.0")

    def execute_test_logic(self) -> Result:
        """
        The 'external_include_paths' toolchain feature automatically moves some include paths in the Bazel
        CompilationContext to the 'external_includes' list so they can be provided to the compiler via '-isystem'.
        This allows silencing compiler warnings originating from those external headers.
        """
        expected = ExpectedResult(success=True)
        actual = self._run_dwyu(
            target=["//complex_includes:all", "@complex_includes_test_repo//..."],
            extra_args=["--features=external_include_paths"],
            aspect=self.default_aspect,
        )

        return self._check_result(actual=actual, expected=expected)
