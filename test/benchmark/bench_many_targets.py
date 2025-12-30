#!/usr/bin/env python3
from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from shutil import rmtree

logging.basicConfig(format="%(message)s", level=logging.INFO)
log = logging.getLogger()

# Allow importing test support code. Relative imports do not work in our case.
# We do this centrally here, so all code we import while executing this knows the extended PYTHONPATH
WS_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(WS_ROOT))

from test.benchmark.lib import common_main, run_benchmark  # noqa: E402

#
# Test Parameters
#

LIBS = 10
LIB_USAGE_PER_DIR = 5
DIRS_REPEATING_THE_PATTERN = 1

ITERATIONS = 1
# No need to restrict jobs in a test for parallel work on a whole workspace
JOBS = -1

#
# Generation templates
#

BENCHMARKS_DIR = WS_ROOT / "test/benchmark"
OUTPUT_DIR = BENCHMARKS_DIR / "generated/many_targets"

LIB_TEMPLATE = """
#ifndef LIB_HEADER_{N}_H
#define LIB_HEADER_{N}_H

#include <array>
#include <iostream>
#include <vector>

void doLibThings_{N}() {{}}

#endif
"""

LIB_USAGE_TEMPLATE = """
{LIB_INCLUDES}

void useLibThings() {{
{LIB_USAGE}
}}
"""

LIB_BUILD = """
load("@rules_cc//cc:cc_library.bzl", "cc_library")

{LIBS_DECLARATIONS}

{LIB_USAGES}
"""

LIB_BUILD_LIB_DECLARATION_BLOCK = 'cc_library(name = "lib_{N}", hdrs = ["lib_{N}.h"])'
LIB_BUILD_LIB_USAGE_BLOCK = 'cc_library(name = "use_libs_{N}", srcs = ["use_libs_{N}.cpp"], deps = [{DEPS}])'

ROOT_BUILD = """
load("@rules_cc//cc:cc_library.bzl", "cc_library")

cc_library(
    name = "primer",
    srcs = ["primer.cpp"],
)
"""


def prepare_base_directory() -> None:
    if OUTPUT_DIR.exists():
        rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True)


def create_test_setup() -> None:
    prepare_base_directory()

    for num_dir in range(DIRS_REPEATING_THE_PATTERN):
        lib_dir = OUTPUT_DIR / f"dir_{num_dir}"
        lib_dir.mkdir()

        for num_lib in range(LIBS):
            (lib_dir / f"lib_{num_lib}.h").write_text(LIB_TEMPLATE.format(N=num_lib))

        ws_relative_include_path = lib_dir.relative_to(WS_ROOT / BENCHMARKS_DIR)
        use_libs_includes = "\n".join(f'#include "{ws_relative_include_path}/lib_{n}.h"' for n in range(LIBS))
        use_libs_calls = "\n".join(f"    doLibThings_{n}();" for n in range(LIBS))
        for n in range(LIB_USAGE_PER_DIR):
            usage_file = lib_dir / f"use_libs_{n}.cpp"
            usage_file.write_text(LIB_USAGE_TEMPLATE.format(LIB_INCLUDES=use_libs_includes, LIB_USAGE=use_libs_calls))

        lib_declarations = "\n".join(LIB_BUILD_LIB_DECLARATION_BLOCK.format(N=n) for n in range(LIBS))
        lib_usage_deps = ", ".join(f'":lib_{n}"' for n in range(LIBS))
        lib_usages = "\n".join(LIB_BUILD_LIB_USAGE_BLOCK.format(N=n, DEPS=lib_usage_deps) for n in range(LIB_USAGE_PER_DIR))
        (lib_dir / "BUILD").write_text(LIB_BUILD.format(LIBS_DECLARATIONS=lib_declarations, LIB_USAGES=lib_usages))

    (OUTPUT_DIR / "primer.cpp").write_text("void doSth() {}")
    (OUTPUT_DIR / "BUILD").write_text(ROOT_BUILD)


def main() -> None:
    """
    Benchmarking many Bazel targets with only a few dependencies and simple code.
    This benchmark ist focused at ensuring that many trivial analysis actions are efficient.
    """
    create_test_setup()

    # Execute the Bazel commands from within the benchmarks workspace
    os.chdir(BENCHMARKS_DIR)

    primer = "//generated/many_targets:primer"
    target = "//generated/many_targets/..."
    run_benchmark(
        aspect="dwyu_legacy_default",
        primer=primer,
        bench_target=target,
        description="Default legacy DWYU",
        iterations=ITERATIONS,
        jobs=JOBS,
    )
    run_benchmark(
        aspect="dwyu_cpp_impl",
        primer=primer,
        bench_target=target,
        description="DWYU C++ implementation",
        iterations=ITERATIONS,
        jobs=JOBS,
    )


if __name__ == "__main__":
    common_main()
    main()
