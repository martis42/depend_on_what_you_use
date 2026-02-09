from test.apply_fixes.test_case import TestCaseBase
from test.support.result import Result, Success


class TestCase(TestCaseBase):
    @property
    def test_target(self) -> str:
        return "//tool_cli/workspace:binary"

    def execute_test_logic(self) -> Result:
        self._create_reports(aspect="//tool_cli/workspace:aspect.bzl%default_aspect")
        # Make buildozer a noop by writing changes to output instead of to the BUILD file. We don't need to limit the
        # processes for the core test logic. We simply do this to test the forwarding of multiple arguments.
        self._run_automatic_fix(extra_args=["--fix-unused", "--buildozer-arg", "-stdout -P=2"])

        target_deps = self._get_target_deps(self.test_target)
        if (expected := {"//tool_cli/workspace:lib"}) != target_deps:
            return self._make_unexpected_deps_error(expected_deps=expected, actual_deps=target_deps)
        return Success()
