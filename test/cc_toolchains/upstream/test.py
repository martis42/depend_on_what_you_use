#!/usr/bin/env python3
from __future__ import annotations

import argparse
import logging
import platform
import subprocess
import sys
from dataclasses import dataclass
from os import chdir
from pathlib import Path
from shlex import join as shlex_join
from tempfile import TemporaryDirectory

# Allow importing test support code. Relative imports do not work in our case.
# We do this centrally here, so all code we import while executing this knows the extended PYTHONPATH
# ruff: noqa: E402
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(WORKSPACE_ROOT))

from test.cc_toolchains.upstream.prepare_workspace import prepare_workspace
from test.support.bazel import (
    get_bazel_binary,
    get_current_workspace,
    get_explicit_bazel_version,
    make_bazel_version_env,
)

logging.basicConfig(format="%(message)s", level=logging.INFO)
log = logging.getLogger(__name__)


@dataclass
class BazelVersion:
    """
    For debugging purposes we want to see which Bazel version exactly was used.
    For test definition and output caches, we want however the dynamic versions (e.g. '42.x' or 'rolling').
    """

    dynamic: str
    resolved: str = ""


@dataclass
class ToolchainConfig:
    name: str
    # Not all toolchains are compatible to all Bazel versions
    bazel_versions: list[BazelVersion]
    # Not all toolchains work with all platforms. Use identifiers as reported by platform.system()
    platforms: list[str]
    # How to depend on the toolchain in the 'MODULE.bazel' file
    module_snippet: str
    # Extra command line args required to use the toolchain
    extra_args: list[str]
    # Document where the toolchain is from
    source: str


TOOLCHAINS = [
    ToolchainConfig(
        name="host_toolchain",
        source="https://github.com/bazelbuild/rules_cc",
        bazel_versions=[BazelVersion("6.4.0"), BazelVersion("7.0.0"), BazelVersion("8.0.0"), BazelVersion("rolling")],
        platforms=["Linux", "Darwin", "Windows"],
        extra_args=[],
        module_snippet="",
    ),
    ToolchainConfig(
        name="toolchains_llvm",
        source="https://github.com/bazel-contrib/toolchains_llvm",
        bazel_versions=[BazelVersion("7.0.0"), BazelVersion("8.0.0"), BazelVersion("rolling")],
        platforms=["Linux", "Darwin"],
        extra_args=["--config=no_default_toolchain"],
        module_snippet="""
bazel_dep(name = "toolchains_llvm", version = "1.4.0")

llvm = use_extension("@toolchains_llvm//toolchain/extensions:llvm.bzl", "llvm")
llvm.toolchain(llvm_version = "19.1.7")
use_repo(llvm, "llvm_toolchain")

register_toolchains("@llvm_toolchain//:all")
""",
    ),
    ToolchainConfig(
        name="toolchains_llvm_bootstrapped",
        source="https://github.com/cerisier/toolchains_llvm_bootstrapped",
        bazel_versions=[BazelVersion("7.0.0"), BazelVersion("8.0.0")],
        # Based on the rules_based approach which seems to not properly set the compiler executable in CcToolchainInfo
        platforms=[],
        extra_args=["--config=no_default_toolchain", "--experimental_cc_static_library"],
        module_snippet="""
bazel_dep(name = "toolchains_llvm_bootstrapped", version = "0.2.4")

register_toolchains("@toolchains_llvm_bootstrapped//toolchain:all")
""",
    ),
    ToolchainConfig(
        name="hermetic_cc_toolchain",
        source="https://github.com/uber/hermetic_cc_toolchain",
        # On GitHub worker das not work with Bazel >= 9.0.0 or 7.0.0 for an unknown reason. Compiler is executable but does provide empty output when called.
        bazel_versions=[BazelVersion("6.4.0"), BazelVersion("7.1.0"), BazelVersion("8.0.0")],
        platforms=["Linux", "Darwin", "Windows"],
        extra_args=["--config=no_default_toolchain"],
        module_snippet="""
bazel_dep(name = "hermetic_cc_toolchain", version = "3.1.0")

toolchains = use_extension("@hermetic_cc_toolchain//toolchain:ext.bzl", "toolchains")
use_repo(toolchains, "zig_sdk")

register_toolchains("@zig_sdk//...")
""",
    ),
    ToolchainConfig(
        name="toolchains_musl",
        source="https://github.com/bazel-contrib/musl-toolchain",
        bazel_versions=[BazelVersion("6.4.0"), BazelVersion("7.0.0"), BazelVersion("8.0.0"), BazelVersion("rolling")],
        # Cannot compile from Darwin to Darwin, just cross compile from Darwin to Linux. Cross compilation is not yet supported/tested though.
        platforms=["Linux"],
        extra_args=["--config=no_default_toolchain"],
        module_snippet="""
bazel_dep(name = "toolchains_musl", version = "0.1.20")
""",
    ),
]


def resolve_bazel_versions(toolchain: ToolchainConfig, bazel_bin: Path) -> None:
    """
    To clearly understand what we are testing, we translate dynamic Bazel versions to fully resolved ones
    """
    for bazel_version in toolchain.bazel_versions:
        bazel_version.resolved = get_explicit_bazel_version(bazel_bin=bazel_bin, dynamic_version=bazel_version.dynamic)


def make_output_base(output_base: Path) -> list[str]:
    """
    For test separation reasons we use temporary virtual workspaces for executing the test commands.
    We use constant output bases so the system is not swamped with abandoned output bases for each temporary workspace.
    Also we can shorten the longish toolchain artifacts extraction time for repeated testing.
    """
    output_base.mkdir(parents=True, exist_ok=True)
    return [f"--output_base={output_base}"]


def run_tests(workspace: Path, bazel_bin: Path, toolchain: ToolchainConfig, use_output_base: bool) -> list[str]:
    log.info(f"\n##\n## Testing toolchain '{toolchain.name}'\n##")
    output_root = Path.home() / ".cache" / "bazel" / "dwyu" / "test_cc_toolchain"
    failures = []

    if platform.system() not in toolchain.platforms:
        log.info(f">> Skipping due to incompatible platform '{platform.system()}'")
        return []

    for bazel_version in toolchain.bazel_versions:
        log.info(f"\n>> Testing with Bazel '{bazel_version.resolved}'")

        output_base_arg = (
            make_output_base(output_root / f"{toolchain.name}_bazel_{bazel_version.dynamic}") if use_output_base else []
        )
        env = make_bazel_version_env(bazel_version.resolved)
        cmd = [
            str(bazel_bin),
            *output_base_arg,
            "--max_idle_secs=10",
            "build",
            "--enable_bzlmod=true",
            "--config=dwyu",
            *toolchain.extra_args,
            "//:use_toolchain_headers",
        ]
        log.info(f">> Executing: {shlex_join(cmd)}\n")
        if subprocess.run(cmd, cwd=workspace, check=False, env=env).returncode != 0:
            failures.append(f"{toolchain.name}: {bazel_version.resolved}")

    return failures


def cli() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--list",
        "-l",
        action="store_true",
        help="List available toolchains",
    )
    parser.add_argument(
        "--toolchain",
        "-t",
        type=str,
        help="Execute only integration tests for this toolchain",
    )
    parser.add_argument(
        "--manifest_repo",
        "-m",
        type=Path,
        help="Instead of running the integration tests, create a permanent workspace for manual testing. Has to be used with '--toolchain'",
    )
    parser.add_argument(
        "--no_output_base",
        action="store_true",
        help="Do not create a dedicated output base per test. Optimizes CI runs for which dedicated outout bases are a slowdown, as the system is either way thrown away.",
    )

    parsed_args = parser.parse_args()
    if parsed_args.manifest_repo and not parsed_args.toolchain:
        log.error("ERROR: '--manifest_repo' has to be used with a specific toolchain provided via '--toolchain'")
        sys.exit(1)

    return parsed_args


def main(args: argparse.Namespace) -> int:
    if args.list:
        log.info("Available toolchains for testing:")
        log.info("\n".join([f"- {t.name}" for t in TOOLCHAINS]))
        return 0

    toolchains_under_test = TOOLCHAINS
    if args.toolchain:
        toolchains_under_test = [t for t in TOOLCHAINS if t.name == args.toolchain]

    bazel_bin = get_bazel_binary()
    dwyu_path = get_current_workspace(bazel_bin)

    if args.manifest_repo:
        prepare_workspace(
            workspace=args.manifest_repo,
            dwyu_path=dwyu_path,
            module_extra_content=toolchains_under_test[0].module_snippet,
        )
        return 0

    failures = []
    for toolchain in toolchains_under_test:
        resolve_bazel_versions(toolchain=toolchain, bazel_bin=bazel_bin)
        # Ignore cleanup errors as otherwise we have problems in windows CI jobs
        with TemporaryDirectory(ignore_cleanup_errors=True) as tmp_workspace:
            prepare_workspace(
                workspace=Path(tmp_workspace), dwyu_path=dwyu_path, module_extra_content=toolchain.module_snippet
            )
            failures.extend(
                run_tests(
                    workspace=Path(tmp_workspace),
                    bazel_bin=bazel_bin,
                    toolchain=toolchain,
                    use_output_base=not args.no_output_base,
                )
            )

    if failures:
        log.info("\nSome CC toolchain integration tests FAILED")
        log.info("\n".join(f"- {fail}" for fail in sorted(failures)))
        return 1

    log.info("\nAll CC toolchain integration tests succeeded")
    return 0


if __name__ == "__main__":
    # Ensure we can invoke the script from various places
    chdir(Path(__file__).parent)

    sys.exit(main(cli()))
