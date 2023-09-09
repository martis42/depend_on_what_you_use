from result import Result, Success
from test_case import TestCaseBase


class TestCase(TestCaseBase):
    @property
    def test_target(self) -> str:
        return "//:binary"

    def execute_test_logic(self) -> Result:
        self._create_reports(extra_args=["--noexperimental_convenience_symlinks", "--compilation_mode=opt"])
        self._run_automatic_fix(extra_args=["--fix-unused", "--use-bazel-info=opt"])

        target_deps = self._get_target_attribute(target=self.test_target, attribute="deps")
        if (expected := set()) != target_deps:
            return self._make_unexpected_deps_error(expected_deps=expected, actual_deps=target_deps)
        else:
            return Success()
