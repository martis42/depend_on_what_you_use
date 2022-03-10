import argparse
import os
import subprocess as sb
from dataclasses import dataclass, field
from typing import Dict, List, Union

# Each line in the output corresponding to an error is expexted to start with this
ERRORS_PREFIX = " " * 2

# DWYU terminal output key fragments
DWYU_FAILURE = "Result: FAILURE"
CATEGORY_INVALID_INCLUDES = "Includes which are not available from the direct dependencies"
CATEGORY_NON_PRIVATE_DEPS = "Public dependencies which are only used in private code"
CATEGORY_UNUSED_DEPS = "Unused dependencies (none of their headers are referenced)"
CATEGORY_UTILIZATION = "Dependencies with utilization below the threshold"


@dataclass
class TestCmd:
    target: str
    aspect: str = ""
    extra_args: List[str] = field(default_factory=list)


@dataclass
class ExpectedResult:
    """
    TODO
    """

    success: bool
    invalid_includes: List[str] = field(default_factory=list)
    unused_deps: List[str] = field(default_factory=list)
    deps_which_should_be_private: List[str] = field(default_factory=list)
    deps_with_low_utilization: List[str] = field(default_factory=list)

    def matches_expectation(self, return_code: int, dwyu_output: str) -> bool:
        if not self._has_correct_status(return_code=return_code, output=dwyu_output):
            return False

        output_lines = dwyu_output.split("\n")
        if not ExpectedResult._has_expected_errors(
            expected_errors=self.invalid_includes,
            error_category=CATEGORY_INVALID_INCLUDES,
            output=output_lines,
        ):
            return False
        if not ExpectedResult._has_expected_errors(
            expected_errors=self.unused_deps,
            error_category=CATEGORY_UNUSED_DEPS,
            output=output_lines,
        ):
            return False
        if not ExpectedResult._has_expected_errors(
            expected_errors=self.deps_which_should_be_private,
            error_category=CATEGORY_NON_PRIVATE_DEPS,
            output=output_lines,
        ):
            return False
        if not ExpectedResult._has_expected_errors(
            expected_errors=self.deps_with_low_utilization,
            error_category=CATEGORY_UTILIZATION,
            output=output_lines,
        ):
            return False

        return True

    def _has_correct_status(self, return_code: int, output: str) -> bool:
        if self.success and return_code == 0:
            return True
        if not self.success and return_code != 0 and DWYU_FAILURE in output:
            return True
        return False

    @staticmethod
    def _has_expected_errors(expected_errors: List[str], error_category: str, output: List[str]) -> bool:
        idx_category = ExpectedResult._find_line_with(lines=output, val=error_category)
        if expected_errors and idx_category is None:
            return False
        if expected_errors:
            # todo idx magic into helper func
            errors_begin = idx_category + 1
            errors_end = 0
            for i in range(errors_begin, len(output)):
                if output[i].startswith(ERRORS_PREFIX):
                    errors_end = i + 1
                else:
                    break
            if not ExpectedResult._has_errors(
                error_lines=output[errors_begin:errors_end], expected_errors=expected_errors
            ):
                return False
        if not expected_errors and not idx_category is None:
            return False

        return True

    @staticmethod
    def _find_line_with(lines: List[str], val: str) -> Union[int, None]:
        for idx, line in enumerate(lines):
            if val in line:
                return idx
        return None

    @staticmethod
    def _has_errors(error_lines: List[str], expected_errors: List[str]) -> bool:
        if len(error_lines) != len(expected_errors):
            return False
        for error in expected_errors:
            if not any(error in line for line in error_lines):
                return False
        return True


@dataclass
class TestCase:
    name: str
    cmd: TestCmd
    expected: ExpectedResult
    min_version: str = ""


@dataclass
class FailedTest:
    name: str
    version: str


def verify_test(test: TestCase, process: sb.CompletedProcess, verbose: bool) -> bool:
    if test.expected.matches_expectation(return_code=process.returncode, dwyu_output=process.stdout):
        if verbose:
            print("\n" + process.stdout + "\n")
        ok_verb = "succeeded" if test.expected.success else "failed"
        print(f"<<< OK '{test.name}' {ok_verb} as expected")
        return True
    else:
        print("\n" + process.stdout + "\n")
        print(f"<<< ERROR '{test.name}' did not behave as expected")
        return False


def make_cmd(test_cmd: TestCmd, extra_args: List[str]) -> List[str]:
    cmd = ["bazelisk", "build", "--noshow_progress"]
    if test_cmd.aspect:
        cmd.extend([f"--aspects={test_cmd.aspect}", "--output_groups=cc_dwyu_output"])
    cmd.extend(extra_args)
    cmd.extend(test_cmd.extra_args)
    cmd.append("--")
    cmd.append(test_cmd.target)
    return cmd


def execute_tests(
    versions: List[str], tests: List[TestCase], version_specific_args: Dict, verbose: bool = False
) -> List[FailedTest]:
    failed_tests = []

    test_env = {}
    test_env["HOME"] = os.getenv("HOME")  # Required by Bazel to determine bazel-out
    test_env["PATH"] = os.getenv("PATH")  # Access to bazelisk

    for version in versions:
        test_env["USE_BAZEL_VERSION"] = version

        extra_args = []
        for args_version, args in version_specific_args.items():
            if args_version <= version:
                extra_args.extend(args)

        for test in tests:
            if test.min_version and test.min_version > version:
                print(f"\n--- Skip '{test.name}' due to incompatible Bazel '{version}'")
                continue
            else:
                print(f"\n>>> Execute '{test.name}' with Bazel '{version}'")

            process = sb.run(
                make_cmd(test_cmd=test.cmd, extra_args=extra_args),
                env=test_env,
                text=True,
                stdout=sb.PIPE,
                stderr=sb.STDOUT,
            )

            if not verify_test(test=test, process=process, verbose=verbose):
                failed_tests.append(FailedTest(name=test.name, version=version))

    return failed_tests


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", "-v", action="store_true", help="Show output of test runs.")
    parser.add_argument("--bazel", "-b", metavar="VERSION", help="Run tests with the specified Bazel version.")
    parser.add_argument("--test", "-t", nargs="+", help="Run the specified test cases.")
    args = parser.parse_args()
    return args


def main(args: argparse.Namespace, test_cases: List[TestCase], test_versions: List[str], version_specific_args: Dict):
    bazel_versions = [args.bazel] if args.bazel else test_versions
    if args.test:
        active_tests = [tc for tc in test_cases if tc.name in args.test]
    else:
        active_tests = test_cases

    failed_tests = execute_tests(
        versions=bazel_versions, tests=active_tests, version_specific_args=version_specific_args, verbose=args.verbose
    )

    print("\n" + 30 * "#" + "  SUMMARY  " + 30 * "#" + "\n")
    if failed_tests:
        print("FAILURE\n")
        print("These tests failed:")
        print("\n".join(f"- '{t.name} - for Bazel version '{t.version}'" for t in failed_tests))
        return 1
    else:
        print("SUCCESS\n")
        return 0
