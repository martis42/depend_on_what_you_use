import json
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

from test.support.result import Error, Result, Success

DWYU_FAILURE = "Result: FAILURE"
DWYU_REPORT = "DWYU Report:"


def normalize_file_path(path: str) -> str:
    """
    On Windows DWYU reports Windows file paths with backslashes, but our tests expect POSIX-style paths with forward slashes.
    """
    # Remove the double baskslash replacing after the Python impl has been removed
    return path.replace("\\\\", "/").replace("\\", "/")


def normalize_file_paths(paths: Iterable[str]) -> list[str]:
    return [normalize_file_path(p) for p in paths]


def normalize_target_name(target: str) -> str:
    """
    For ease of use in test specs we desire the short apparent name style instead of the canonical Bazel target names.
    """
    return target.replace("@@", "@").replace("@//", "//")


def normalize_target_names(target: Iterable[str]) -> list[str]:
    return [normalize_target_name(t) for t in target]


@dataclass
class ExpectedDwyuFailure:
    target: str
    invalid_includes: dict[str, list[str]] = field(default_factory=dict)
    unused_public_deps: list[str] = field(default_factory=list)
    unused_private_deps: list[str] = field(default_factory=list)
    deps_which_should_be_private: list[str] = field(default_factory=list)

    def check_expectation(self, report_data: dict) -> bool:
        reported_public_includes_without_dep = report_data.get("public_includes_without_dep", {})
        reported_private_includes_without_dep = report_data.get("private_includes_without_dep", {})
        reported_invalid_includes = {**reported_public_includes_without_dep, **reported_private_includes_without_dep}
        if set(normalize_file_paths(reported_invalid_includes.keys())) != set(self.invalid_includes.keys()):
            return False
        for src_file, includes in reported_invalid_includes.items():
            if set(self.invalid_includes.get(normalize_file_path(src_file), [])) != set(includes):
                return False

        if set(self.unused_public_deps) != set(normalize_target_names(report_data.get("unused_deps", []))):
            return False

        if set(self.unused_private_deps) != set(
            normalize_target_names(report_data.get("unused_implementation_deps", []))
        ):
            return False

        return set(self.deps_which_should_be_private) == set(
            normalize_target_names(report_data.get("deps_which_should_be_private", []))
        )


@dataclass
class ExpectedResult:
    """
    Encapsulates an expected result of a DWYU analysis and offers functions
    to compare a given output to the expectations.
    """

    def __init__(self, success: bool, failures: list[ExpectedDwyuFailure]) -> None:
        self.failures = failures or []
        self.success = success

    def matches_expectation(self, return_code: int, dwyu_output: str, reports_root: Path) -> Result:  # noqa: PLR0911
        if not self._has_correct_status(return_code=return_code, output=dwyu_output):
            return Error("unexpected DWYU status code")

        if self.success:
            # No further checks needed for successful runs
            return Success()

        all_report_paths = [
            line.split(DWYU_REPORT)[1].strip() for line in dwyu_output.splitlines() if DWYU_REPORT in line
        ]
        all_reports = {}
        for report in all_report_paths:
            report_file = reports_root / report
            if not report_file.exists():
                return Error(f"missing DWYU report file: {report_file}")
            data = json.loads(report_file.read_text())
            all_reports[normalize_target_name(data["analyzed_target"])] = data

        if len(self.failures) != len(all_report_paths):
            return Error("number of DWYU reports does not match expected failures")

        for expected_failure in self.failures:
            expected_target = normalize_target_name(expected_failure.target)
            if expected_target not in all_reports:
                return Error("missing report for expected failure")
            if not expected_failure.check_expectation(all_reports[expected_target]):
                return Error("found unexpected DWYU results")

        return Success()

    def _has_correct_status(self, return_code: int, output: str) -> bool:
        if self.success and return_code == 0:
            return True
        # Ensuring 'DWYU_FAILURE' is in the output prevents overlooking failure due to unrelated issues
        return not self.success and return_code != 0 and DWYU_FAILURE in output


class ExpectedSuccess(ExpectedResult):
    def __init__(self) -> None:
        super().__init__(success=True, failures=[])


class ExpectedFailure(ExpectedResult):
    def __init__(self, failures: ExpectedDwyuFailure | list[ExpectedDwyuFailure]) -> None:
        super().__init__(success=False, failures=[failures] if isinstance(failures, ExpectedDwyuFailure) else failures)
