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

# Allow importing test support code. Relative imports do not work in our case.
# We do this centrally here, so all code we import while executing this knows the extended PYTHONPATH
# ruff: noqa: E402
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WORKSPACE_ROOT))

from test.support.bazel import get_bazel_binary

logging.basicConfig(format="%(message)s", level=logging.INFO)
log = logging.getLogger(__name__)


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


def make_cmd(example: Example, bazel_bin: str, legacy_workspace: bool) -> list[str]:
    cmd = [bazel_bin, "build"]
    if legacy_workspace:
        cmd.extend(["--noenable_bzlmod", "--enable_workspace"])
    cmd.extend(shlex.split(example.build_cmd))
    return cmd


def execute_example(example: Example, bazel_bin: str, legacy_workspace: bool) -> Result:
    cmd = make_cmd(example=example, bazel_bin=bazel_bin, legacy_workspace=legacy_workspace)
    cmd_str = shlex.join(cmd)
    log.info(f"\n##\n## Executing: '{cmd_str}'\n##\n")

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
    parser.add_argument(
        "--bazel-bin",
        "-b",
        type=str,
        help="""
Manually define the Bazel binary used by the test commands instead of automatically discovering and ensuring bazelisk.
This is relevant for test environments outside our control managing Bazel versions for testing without bazelisk.
""".strip(),
    )
    return parser.parse_args()


def main(args: Namespace) -> int:
    """
    Basic testing if the examples behave as desired.

    We ony look for the return code of a command. If a command fails as expected we do not analyze if it fails for the
    correct reason. These kind of detailed testing is done in the aspect integration tests.
    """
    bazel_binary = args.bazel_bin if args.bazel_bin else str(get_bazel_binary())

    results = [
        execute_example(example=ex, bazel_bin=bazel_binary, legacy_workspace=args.legacy_workspace) for ex in EXAMPLES
    ]
    failed_examples = [res.example for res in results if not res.success]

    if failed_examples:
        log.info("\nFAILURE: The following examples did not behave as expected:")
        log.info("\n".join(f"- {failed}" for failed in failed_examples))
        return 1

    log.info("\nSUCCESS: All examples behaved as expected")
    return 0


if __name__ == "__main__":
    args = cli()

    # Ensure we can invoke the script from various places
    chdir(Path(__file__).parent)

    sys.exit(main(args))
