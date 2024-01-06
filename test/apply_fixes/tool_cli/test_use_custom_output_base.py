from tempfile import TemporaryDirectory

from result import Result, Success
from test_case import TestCaseBase


class TestCase(TestCaseBase):
    @property
    def test_target(self) -> str:
        return "//:binary"

    def execute_test_logic(self) -> Result:
        with TemporaryDirectory() as output_base:
            self._create_reports(startup_args=[f"--output_base={output_base}"])
            self._run_automatic_fix(extra_args=["--fix-unused", f"--bazel-bin={output_base}"])

            target_deps = self._get_target_attribute(target=self.test_target, attribute="deps")
            if (expected := set()) != target_deps:  # type: ignore[var-annotated]
                return self._make_unexpected_deps_error(expected_deps=expected, actual_deps=target_deps)
            return Success()
