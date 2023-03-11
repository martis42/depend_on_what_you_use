from result import Error, Result, Success
from test_case import TestCaseBase


class TestCase(TestCaseBase):
    @property
    def test_target(self) -> str:
        return "//:use_libs"

    def execute_test_logic(self) -> Result:
        self._create_reports()
        self._run_automatic_fix(extra_args=["--fix-missing-deps"])

        target_deps = self._get_target_attribute(target=self.test_target, attribute="deps")
        if target_deps == {"//:libs_provider", "//libs:foo", "//libs:bar", "//:root_file_lib"}:
            return Success()
        else:
            return Error(f"Dependencies have not been adapted correctly. Unexpected dependencies: {target_deps}")
