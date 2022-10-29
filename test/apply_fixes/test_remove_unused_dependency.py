from src.result import Error, Result, Success
from src.test_case import TestCaseBase


class TestCase(TestCaseBase):
    @property
    def test_target(self) -> str:
        return "//:main"

    def execute_test_logic(self) -> Result:
        self._create_reports()
        self._run_automatic_fix()
        target_deps = self._get_target_attribute(target=self.test_target, attribute="deps")

        if target_deps == {"//:used"}:
            return Success()
        else:
            return Error(f"Dependencies have not been adapted correctly. Unexpected dependencies: {target_deps}")
