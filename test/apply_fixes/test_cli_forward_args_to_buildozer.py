from src.result import Error, Result, Success
from src.test_case import TestCaseBase


class TestCase(TestCaseBase):
    @property
    def test_target(self) -> str:
        return "//:unused_public_dep"

    def execute_test_logic(self) -> Result:
        self._create_reports()
        # Make buildozer a noop by writing changes to output instead of to the BUILD file
        self._run_automatic_fix(extra_args=["--buildozer-args", "-stdout"])
        target_deps = self._get_target_attribute(target=self.test_target, attribute="deps")

        if target_deps == {"//:lib_a", "//:lib_b", "//:lib_c"}:
            return Success()
        else:
            return Error(f"Dependencies have been adapted instead of remaining untouched. Dependencies: {target_deps}")
