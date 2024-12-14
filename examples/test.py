#!/usr/bin/env python3
from __future__ import annotations

import logging
import shlex
import subprocess
import sys
from argparse import ArgumentParser, Namespace
from dataclasses import dataclass
from os import chdir
from pathlib import Path
from shutil import which

logging.basicConfig(format="%(message)s", level=logging.INFO)


@dataclass
class Example:
    build_cmd: str
    expected_success: bool


EXAMPLES = [
    Example(
        build_cmd="--aspects=//:aspect.bzl%dwyu --output_groups=dwyu //basic_usage:correct_dependencies",
        expected_success=True,
    ),
    Example(
        build_cmd="--aspects=//:aspect.bzl%dwyu --output_groups=dwyu //basic_usage:false_dependencies",
        expected_success=False,
    ),
    Example(
        build_cmd="--aspects=//:aspect.bzl%dwyu --output_groups=dwyu //basic_usage:not_using_lib",
        expected_success=False,
    ),
    Example(
        build_cmd="--aspects=//:aspect.bzl%dwyu_ignoring_includes --output_groups=dwyu //ignoring_includes:use_unavailable_headers",
        expected_success=True,
    ),
    Example(
        build_cmd="--aspects=//:aspect.bzl%dwyu --output_groups=dwyu //recursion:use_lib",
        expected_success=True,
    ),
    Example(
        build_cmd="--aspects=//:aspect.bzl%dwyu_recursive --output_groups=dwyu //recursion:use_lib",
        expected_success=False,
    ),
    Example(
        build_cmd="//rule_using_dwyu:dwyu",
        expected_success=False,
    ),
    Example(
        build_cmd="--aspects=//:aspect.bzl%dwyu_set_cplusplus --output_groups=dwyu //set_cpp_standard:cpp_lib",
        expected_success=True,
    ),
    Example(
        build_cmd="--aspects=//:aspect.bzl%dwyu_set_cplusplus --output_groups=dwyu //set_cpp_standard:use_specific_cpp_standard",
        expected_success=True,
    ),
    Example(
        build_cmd="--aspects=//:aspect.bzl%dwyu --output_groups=dwyu //skipping_targets:bad_target",
        expected_success=False,
    ),
    Example(
        build_cmd="--aspects=//:aspect.bzl%dwyu --output_groups=dwyu //skipping_targets:bad_target_skipped",
        expected_success=True,
    ),
    Example(
        build_cmd="--aspects=//:aspect.bzl%dwyu_custom_skipping --output_groups=dwyu //skipping_targets:bad_target_custom_skip",
        expected_success=True,
    ),
    Example(
        build_cmd="--aspects=//:aspect.bzl%dwyu_recursive_skip_external --output_groups=dwyu //skipping_targets:use_broken_external_dependency",
        expected_success=True,
    ),
    Example(
        build_cmd="--aspects=//:aspect.bzl%dwyu_map_specific_deps --output_groups=dwyu //target_mapping:use_lib_b",
        expected_success=True,
    ),
    Example(
        build_cmd="--aspects=//:aspect.bzl%dwyu_map_direct_deps --output_groups=dwyu //target_mapping:use_lib_b",
        expected_success=True,
    ),
    Example(
        build_cmd="--aspects=//:aspect.bzl%dwyu_map_direct_deps --output_groups=dwyu //target_mapping:use_lib_c",
        expected_success=False,
    ),
    Example(
        build_cmd="--aspects=//:aspect.bzl%dwyu_map_transitive_deps --output_groups=dwyu //target_mapping:use_lib_c",
        expected_success=True,
    ),
]


@dataclass
class Result:
    example: str
    success: bool


def get_bazel_binary() -> Path:
    """
    We use bazelisk to control the exact Bazel version we test with. Using the native bazel binary would cause the tests
    to run with an arbitrary Bazel version without us noticing.
    """
    if bazel := which("bazelisk"):
        return Path(bazel)

    # Might be system where bazlisk was renamed to bazel or bazel links to a bazelisk binary not being on PATH.
    # We test this by using the '--strict' option which only exists for bazelisk, but not bazel
    bazel = which("bazel")
    if bazel and (
        subprocess.run([bazel, "--strict", "--version"], shell=False, check=False, capture_output=True).returncode == 0
    ):
        return Path(bazel)

    raise RuntimeError("No bazelisk binary or bazel symlink towards bazelisk available on your system")


def make_cmd(example: Example, bazel_bin: Path, legacy_workspace: bool) -> list[str]:
    cmd = [str(bazel_bin), "build"]
    if legacy_workspace:
        cmd.append("--noenable_bzlmod")
    cmd.extend(shlex.split(example.build_cmd))
    return cmd


def execute_example(example: Example, bazel_bin: Path, legacy_workspace: bool) -> Result:
    cmd = make_cmd(example=example, bazel_bin=bazel_bin, legacy_workspace=legacy_workspace)
    cmd_str = shlex.join(cmd)
    logging.info(f"\n##\n## Executing: '{cmd_str}'\n##\n")

    process = subprocess.run(cmd, check=False)
    if (process.returncode == 0 and example.expected_success) or (
        process.returncode != 0 and not example.expected_success
    ):
        return Result(example=cmd_str, success=True)
    return Result(example=cmd_str, success=False)


def cli() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument(
        "--legacy-workspace",
        "-w",
        action="store_true",
        help="Use the WORKSPACE file based project setup instead of bzlmod.",
    )
    return parser.parse_args()


def main(legacy_workspace: bool) -> int:
    """
    Basic testing if the examples behave as desired.

    We ony look for the return code of a command. If a command fails as expected we do not analyze if it fails for the
    correct reason. These kind of detailed testing is done in the aspect integration tests.
    """
    bazel_binary = get_bazel_binary()

    results = [
        execute_example(example=ex, bazel_bin=bazel_binary, legacy_workspace=legacy_workspace) for ex in EXAMPLES
    ]
    failed_examples = [res.example for res in results if not res.success]

    if failed_examples:
        logging.info("\nFAILURE: The following examples did not behave as expected:")
        logging.info("\n".join(f"- {failed}" for failed in failed_examples))
        return 1

    logging.info("\nSUCCESS: All examples behaved as expected")
    return 0


if __name__ == "__main__":
    args = cli()

    # Ensure we can invoke the script from various places
    chdir(Path(__file__).parent)

    sys.exit(main(args.legacy_workspace))
