from __future__ import annotations

import logging
import subprocess
from importlib.machinery import SourceFileLoader
from pathlib import Path
from re import fullmatch

from test_case import TestCaseBase
from version import CompatibleVersions, TestedVersions

from test.support.bazel import (
    get_bazel_binary,
    get_current_workspace,
    get_explicit_bazel_version,
    make_bazel_version_env,
)
from test.support.result import Error

log = logging.getLogger()


def get_reports_root(bazel_bin: Path, version: str, output_base: Path | None) -> Path:
    out_base = [f"--output_base={output_base}"] if output_base else []
    cmd = [
        str(bazel_bin),
        *out_base,
        "--ignore_all_rc_files",
        # Make sure no idle server lives forever wasting RAM
        "--max_idle_secs=10",
        "info",
        "--experimental_convenience_symlinks=ignore",
        "execution_root",
    ]
    test_env = make_bazel_version_env(version)
    process = subprocess.run(cmd, env=test_env, shell=False, check=True, capture_output=True, text=True)

    return Path(process.stdout.strip())


def execute_test(
    test: TestCaseBase,
    version: TestedVersions,
    bazel_bin: Path,
    output_base: Path | None,
    extra_args: list[str],
    reports_root: Path,
) -> bool:
    if not test.compatibility.is_compatible:
        log.info(f"--- Skip '{test.name}' due to: {test.compatibility.reason}\n")
        return True

    log.info(f">>> Test '{test.name}' with Bazel {version.bazel}")

    succeeded = False
    result = None
    try:
        result = test.execute_test(
            version=version,
            bazel_bin=bazel_bin,
            output_base=output_base,
            extra_args=extra_args,
            reports_root=reports_root,
        )
    except Exception:
        log.exception("Test failed due to exception:")

    if result is None:
        result = Error("No result")

    if result.is_success():
        succeeded = True
    else:
        log.info(result.error)
    log.info(f"<<< {'OK' if succeeded else 'FAILURE'}\n")

    return succeeded


def make_bazel_versions_explicit(versions: list[TestedVersions], bazel_bin: Path) -> list[TestedVersions]:
    """
    We want to utilize dynamic version references like 'rolling' or '42.x'. However, for debugging and caching we
    prefer using concrete version numbers in the test orchestration logic. Thus, we resolve the dynamic version
    identifiers before using them.
    """
    log.info("Parsing Bazel versions:")
    for version in versions:
        if not fullmatch(r"\d+\.\d+\.\d+", version.bazel):
            dynamic_version = version.bazel
            version.bazel = get_explicit_bazel_version(bazel_bin=bazel_bin, dynamic_version=dynamic_version)
            log.info(f"{dynamic_version} -> {version.bazel}")
        else:
            log.info(version.bazel)
    return versions


def file_to_test_name(test_file: Path) -> str:
    return test_file.parent.name + "/" + test_file.stem.replace("test_", "", 1)


def prepare_output_base(version: TestedVersions) -> Path:
    output_root = Path.home() / ".cache" / "bazel" / "dwyu"
    output_base = output_root / f"aspect_integration_tests_bazel_{version.bazel}"
    output_base.mkdir(parents=True, exist_ok=True)
    return output_base


def main(
    tested_versions: list[TestedVersions],
    version_specific_args: dict[str, CompatibleVersions],
    bazel: str | None = None,
    requested_tests: list[str] | None = None,
    list_tests: bool = False,
    cpp_impl_based: bool = False,
    only_default_version: bool = False,
    no_output_base: bool = False,
    verbose: bool = False,
) -> int:
    bazel_binary = get_bazel_binary()
    workspace_path = get_current_workspace(bazel_binary)
    test_files = sorted([Path(x) for x in workspace_path.glob("*/test_*.py")])

    if list_tests:
        test_names = [file_to_test_name(test) for test in test_files]
        log.info("Available test cases:")
        log.info("\n".join(f"- {t}" for t in test_names))
        return 0

    tests = []
    for test in test_files:
        name = file_to_test_name(test)
        if (requested_tests and any(requested in name for requested in requested_tests)) or (not requested_tests):
            module = SourceFileLoader("", str(test.resolve())).load_module()
            tests.append(module.TestCase(name=name, cpp_impl_based=cpp_impl_based, verbose=verbose))

    if bazel:
        versions = [TestedVersions(bazel=bazel)]
    elif only_default_version:
        versions = [version for version in tested_versions if version.is_default]
    else:
        versions = tested_versions

    versions = make_bazel_versions_explicit(versions=versions, bazel_bin=bazel_binary)

    failed_tests = []
    for version in versions:
        log.info(f"""
###
### Aspect integration tests based on Bazel '{version.bazel}'
###
""")

        output_base = prepare_output_base(version) if not no_output_base else None
        reports_root = get_reports_root(bazel_bin=bazel_binary, version=version.bazel, output_base=output_base)
        extra_args = [
            arg
            for arg, valid_versions in version_specific_args.items()
            if valid_versions.is_compatible_to(version.bazel)
        ]
        failed_tests.extend(
            [
                f"'{test.name}' for Bazel {version.bazel}"
                for test in tests
                if not execute_test(
                    test=test,
                    version=version,
                    bazel_bin=bazel_binary,
                    output_base=output_base,
                    extra_args=extra_args,
                    reports_root=reports_root,
                )
            ]
        )

    log.info(f"Running tests {'FAILED' if failed_tests else 'SUCCEEDED'}")
    if failed_tests:
        log.info("\nFailed tests:")
        log.info("\n".join(f"- {failed}" for failed in failed_tests))
        return 1

    return 0
