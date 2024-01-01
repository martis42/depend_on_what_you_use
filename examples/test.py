#!/usr/bin/env python3

import logging
import shlex
import subprocess
import sys
from dataclasses import dataclass

logging.basicConfig(format="%(message)s", level=logging.INFO)


@dataclass
class Example:
    cmd: str
    expected_success: bool


EXAMPLES = [
    Example(
        cmd="bazel build --aspects=//:aspect.bzl%dwyu --output_groups=dwyu //basic_usage:correct_dependencies",
        expected_success=True,
    ),
    Example(
        cmd="bazel build --aspects=//:aspect.bzl%dwyu --output_groups=dwyu //basic_usage:false_dependencies",
        expected_success=False,
    ),
    Example(
        cmd="bazel build --aspects=//:aspect.bzl%dwyu --output_groups=dwyu //basic_usage:not_using_lib",
        expected_success=False,
    ),
    Example(
        cmd="bazel build --aspects=//:aspect.bzl%dwyu_ignoring_includes --output_groups=dwyu //ignoring_includes:use_unavailable_headers",
        expected_success=True,
    ),
    Example(
        cmd="bazel build --aspects=//:aspect.bzl%dwyu --output_groups=dwyu //recursion:use_lib",
        expected_success=True,
    ),
    Example(
        cmd="bazel build --aspects=//:aspect.bzl%dwyu_recursive --output_groups=dwyu //recursion:use_lib",
        expected_success=False,
    ),
    Example(
        cmd="bazel build //rule_using_dwyu/...",
        expected_success=False,
    ),
    Example(
        cmd="bazel build --aspects=//:aspect.bzl%dwyu --output_groups=dwyu //skipping_targets:bad_target",
        expected_success=False,
    ),
    Example(
        cmd="bazel build --aspects=//:aspect.bzl%dwyu --output_groups=dwyu //skipping_targets:bad_target_skipped",
        expected_success=True,
    ),
    Example(
        cmd="bazel build --aspects=//:aspect.bzl%dwyu_custom_skipping --output_groups=dwyu //skipping_targets:bad_target_custom_skip",
        expected_success=True,
    ),
    Example(
        cmd="bazel build --aspects=//:aspect.bzl%dwyu_map_specific_deps --output_groups=dwyu //target_mapping:use_lib_b",
        expected_success=True,
    ),
    Example(
        cmd="bazel build --aspects=//:aspect.bzl%dwyu_map_direct_deps --output_groups=dwyu //target_mapping:use_lib_b",
        expected_success=True,
    ),
    Example(
        cmd="bazel build --aspects=//:aspect.bzl%dwyu_map_direct_deps --output_groups=dwyu //target_mapping:use_lib_c",
        expected_success=False,
    ),
    Example(
        cmd="bazel build --aspects=//:aspect.bzl%dwyu_map_transitive_deps --output_groups=dwyu //target_mapping:use_lib_c",
        expected_success=True,
    ),
]


@dataclass
class Result:
    example: str
    success: bool


def execute_example(example: Example) -> Result:
    logging.info(f"\n##\n## Executing: {example.cmd}\n##\n")

    process = subprocess.run(shlex.split(example.cmd), check=False)
    if (process.returncode == 0 and example.expected_success) or (
        process.returncode != 0 and not example.expected_success
    ):
        return Result(example=example.cmd, success=True)
    return Result(example=example.cmd, success=False)


def main() -> int:
    """
    Basic testing if the examples behave as desired.

    We ony look for the return code of a command. If a command fails as expected we do not analyze if it fails for the
    correct reason. These kind of detailed testing is done in the integration tests.
    """
    results = [execute_example(ex) for ex in EXAMPLES]
    failed_examples = [res.example for res in results if not res.success]

    if failed_examples:
        logging.info("\nFAILURE: The following examples did not behave as expected:")
        logging.info("\n".join(f"- {failed}" for failed in failed_examples))
        return 1

    logging.info("\nSUCCESS: All examples behaved as expected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
