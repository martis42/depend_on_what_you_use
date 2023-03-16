from result import Error, Result, Success
from test_case import TestCaseBase


class TestCase(TestCaseBase):
    @property
    def test_target(self) -> str:
        return "//:mixed_libs_usage"

    def execute_test_logic(self) -> Result:
        self._create_reports(
            aspect="use_implementation_deps_aspect", extra_args=["--experimental_cc_implementation_deps"]
        )
        self._run_automatic_fix(extra_args=["--fix-missing-deps"])

        target_deps = self._get_target_attribute(target=self.test_target, attribute="deps")
        target_implementation_deps = self._get_target_attribute(
            target=self.test_target, attribute="implementation_deps"
        )
        if target_deps == {"//:libs_provider", "//libs:foo", "//:root_file_lib"} and target_implementation_deps == {
            "//libs:bar"
        }:
            return Success()
        else:
            return Error(
                f"Dependencies have not been adapted correctly. Unexpected dependencies:\n"
                + f"  deps: {target_deps}\n"
                + f"  implementation_deps: {target_implementation_deps}"
            )
