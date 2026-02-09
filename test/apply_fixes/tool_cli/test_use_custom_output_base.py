from platform import system
from tempfile import TemporaryDirectory

from test.apply_fixes.test_case import TestCaseBase
from test.support.result import Result, Success


class TestCase(TestCaseBase):
    @property
    def test_target(self) -> str:
        return "//tool_cli/workspace:binary"

    @property
    def is_incompatible(self) -> str:
        """
        Setting a custom output base to a temporary directory does not work as expected on Windows. Cleaning up the
        directory fails. We could not identify the underlying problem yet. As this is a test for an edge case and not a
        major use case, we skip this test for now on Windows.
        """
        if system() == "Windows":
            return "Test is incompatible with Windows"
        return ""

    def execute_test_logic(self) -> Result:
        with TemporaryDirectory() as output_base:
            self._create_reports(
                aspect="//tool_cli/workspace:aspect.bzl%default_aspect", startup_args=[f"--output_base={output_base}"]
            )
            self._run_automatic_fix(
                extra_args=["--fix-unused", f"--search-path={output_base}"], custom_dwyu_report_discovery=True
            )

            target_deps = self._get_target_deps(self.test_target)
            if (expected := set()) != target_deps:
                return self._make_unexpected_deps_error(expected_deps=expected, actual_deps=target_deps)
            return Success()
