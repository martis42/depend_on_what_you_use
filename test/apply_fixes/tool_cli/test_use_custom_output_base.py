from tempfile import TemporaryDirectory

from test.apply_fixes.result import Result, Success
from test.apply_fixes.test_case import TestCaseBase


class TestCase(TestCaseBase):
    @property
    def test_target(self) -> str:
        return "//:binary"

    @property
    def windows_compatible(self) -> bool:
        """
        Setting a custom output base to a temporary directory does not work as expected on Windows. Cleaning up the
        directory fails. We could not identify the underlying problem yet. As this is a test for an edge case and not a
        major use case, we skip this test for now on Windows.
        """
        return False

    def execute_test_logic(self) -> Result:
        with TemporaryDirectory() as output_base:
            self._create_reports(startup_args=[f"--output_base={output_base}"])
            self._run_automatic_fix(extra_args=["--fix-unused", f"--search-path={output_base}"])

            target_deps = self._get_target_attribute(target=self.test_target, attribute="deps")
            if (expected := set()) != target_deps:  # type: ignore[var-annotated]
                return self._make_unexpected_deps_error(expected_deps=expected, actual_deps=target_deps)
            return Success()
