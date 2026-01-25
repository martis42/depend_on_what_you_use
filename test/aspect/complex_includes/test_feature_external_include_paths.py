from expected_result import ExpectedSuccess
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        """
        The 'external_include_paths' toolchain feature automatically moves some include paths in the Bazel
        CompilationContext to the 'external_includes' list so they can be provided to the compiler via '-isystem'.
        This allows silencing compiler warnings originating from those external headers.
        """
        actual = self._run_dwyu(
            target=["//complex_includes:all", "@complex_includes_test_repo//..."],
            extra_args=["--features=external_include_paths"],
            aspect=self.default_aspect,
        )

        return self._check_result(actual=actual, expected=ExpectedSuccess())
