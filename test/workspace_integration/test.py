#!/usr/bin/env python3
from __future__ import annotations

import logging
import subprocess
import sys
from os import chdir
from pathlib import Path
from shlex import join as shlex_join

# Allow importing test support code. Relative imports do not work in our case.
# We do this centrally here, so all code we import while executing this knows the extended PYTHONPATH
# ruff: noqa: E402
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(WORKSPACE_ROOT))

from test.support.bazel import get_bazel_binary, get_explicit_bazel_version, make_bazel_version_env

logging.basicConfig(format="%(message)s", level=logging.INFO)
log = logging.getLogger()

BAZEL_VERSIONS_UNDER_TEST = [
    "6.4.0",
    "7.0.0",
    "7.5.0",
    "8.0.0",
    "8.0.1",
    "rolling",
]

ASPECT_TEST_CMD = ["--aspects=//:aspect.bzl%dwyu_aspect", "--output_groups=dwyu", "//:valid_target"]


def run_tests(is_bzlmod: bool, bazel_versions: list[str]) -> list[str]:
    bzlmod_arg = ["--enable_bzlmod=true"] if is_bzlmod else ["--enable_bzlmod=false"]
    workspace_arg = [] if is_bzlmod else ["--enable_workspace=true"]
    mode = "bzlmod" if is_bzlmod else "WORKSPACE"
    failures = []

    log.info(f"\n##\n## Testing {mode} setup\n##")
    for bazel_version in bazel_versions:
        log.info(f"\n## Testing {mode} with Bazel '{bazel_version}'")

        env = make_bazel_version_env(bazel_version)
        enable_workspace = workspace_arg if bazel_version >= "8.0.0" else []
        cmd = ["bazel", "--max_idle_secs=10", "build", *bzlmod_arg, *enable_workspace, *ASPECT_TEST_CMD]
        log.info(f"## Executing: {shlex_join(cmd)}\n")
        if subprocess.run(cmd, check=False, env=env).returncode != 0:
            failures.append(f"{mode}: {bazel_version}")

    return failures


def resolve_bazel_versions(dynamic_versions: list[str], bazel_bin: Path) -> list[str]:
    """
    To clearly understand what we are testing, we translate dynamic Bazel versions to fully resolved ones
    """
    return [get_explicit_bazel_version(bazel_bin=bazel_bin, dynamic_version=version) for version in dynamic_versions]


def main() -> int:
    bazel_bin = get_bazel_binary()
    bazel_versions = resolve_bazel_versions(dynamic_versions=BAZEL_VERSIONS_UNDER_TEST, bazel_bin=bazel_bin)

    failures = run_tests(is_bzlmod=True, bazel_versions=bazel_versions)
    failures.extend(run_tests(is_bzlmod=False, bazel_versions=bazel_versions))

    if failures:
        log.info("\nSome workspace integration tests FAILED")
        log.info("\n".join(f"- {fail}" for fail in sorted(failures)))
        return 1

    log.info("\nAll workspace integration tests succeeded")
    return 0


if __name__ == "__main__":
    # Ensure we can invoke the script from various places
    chdir(Path(__file__).parent)

    sys.exit(main())
