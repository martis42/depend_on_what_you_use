from result import Error, Result, Success
from test_case import TestCaseBase


class TestCase(TestCaseBase):
    @property
    def test_target(self) -> str:
        return "//:binary"

    def execute_test_logic(self) -> Result:
        self._create_reports(extra_args=["--noexperimental_convenience_symlinks"])
        self._run_automatic_fix(extra_args=["--fix-unused", "--use-bazel-info"])
        target_deps = self._get_target_attribute(target=self.test_target, attribute="deps")

        if target_deps == set():
            return Success()
        else:
            return Error(f"Dependencies have not been adapted correctly. Unexpected dependencies: {target_deps}")
