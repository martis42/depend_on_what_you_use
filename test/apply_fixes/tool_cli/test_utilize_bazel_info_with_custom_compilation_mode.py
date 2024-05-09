from result import Result, Success
from test_case import TestCaseBase


class TestCase(TestCaseBase):
    @property
    def test_target(self) -> str:
        return "//:binary"

    def execute_test_logic(self) -> Result:
        self._create_reports(extra_args=["--noexperimental_convenience_symlinks", "--compilation_mode=opt"])
        # The remote cache arg has no meaning for the test behavior. It is only used to check that parsing multiple
        # arguments from one string works without error.
        self._run_automatic_fix(
            extra_args=["--fix-unused", "--use-bazel-info", "--bazel-args", "--remote_cache= -c opt"]
        )

        target_deps = self._get_target_attribute(target=self.test_target, attribute="deps")
        if (expected := set()) != target_deps:  # type: ignore[var-annotated]
            return self._make_unexpected_deps_error(expected_deps=expected, actual_deps=target_deps)
        return Success()
