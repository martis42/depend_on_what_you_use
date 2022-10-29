from src.result import Error, Result, Success
from src.test_case import TestCaseBase


class TestCase(TestCaseBase):
    @property
    def test_target(self) -> str:
        return "//:main"

    def execute_test_logic(self) -> Result:
        self._create_reports(extra_args=["--noexperimental_convenience_symlinks", "--compilation_mode=opt"])
        self._run_automatic_fix(extra_args=["--use-bazel-info=opt"])
        target_deps = self._get_target_attribute(target=self.test_target, attribute="deps")

        if target_deps == {"//:used"}:
            return Success()
        else:
            return Error(f"Dependencies have not been adapted correctly. Unexpected dependencies: {target_deps}")
