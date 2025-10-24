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

TEST_CASES = 5000

ITERATIONS = 3
JOBS = 1

#
# Generation templates
#

BENCHMARKS_DIR = WS_ROOT / "test/benchmark"
OUTPUT_DIR = BENCHMARKS_DIR / "generated/complex_code"

TEMPLATE = """
#include "gmock/gmock.h"
#include "gtest/gtest.h"

#include <vector>
#include <algorithm>

std::vector<int> CreateList(int magic) {{
    std::vector<int> foo{{magic}};
    std::fill(foo.begin(), foo.end(), 42);
    std::transform(foo.begin(), foo.end(), foo.begin(), [](int v) {{ return (v * v) - 1337; }});
    return foo;
}}

{TESTS}
"""

TEST_CASE = """
TEST(TEST_{N}, SOME_DESCRIPTION_{N}) {{
    const auto result = CreateList({N});
    EXPECT_THAT(result, ::testing::ElementsAre(13, 37, 42));
}}
"""

PRIMER = """
#include "gtest/gtest.h"

void SomeFn() {}
"""

BUILD_FILE = """
load("@rules_cc//cc:cc_test.bzl", "cc_test")
load("@rules_cc//cc:cc_library.bzl", "cc_library")

cc_test(
    name = "benchmark",
    srcs = ["main.cpp"],
    deps = [
        "@googletest//:gtest",
        "@googletest//:gtest_main",
    ],
    defines=["__cplusplus=201703"],
)

cc_library(
    name = "primer",
    srcs = ["primer.cpp"],
    deps = [
        "@googletest//:gtest",
        "@googletest//:gtest_main",
    ],
    defines=["__cplusplus=201703"],
)
""".lstrip()


def prepare_directory_layout() -> None:
    if OUTPUT_DIR.exists():
        rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True)


def create_test_setup() -> None:
    prepare_directory_layout()

    tests = ""
    for n in range(TEST_CASES):
        tests += TEST_CASE.format(N=n)
    (OUTPUT_DIR / "main.cpp").write_text(TEMPLATE.format(TESTS=tests))

    (OUTPUT_DIR / "primer.cpp").write_text(PRIMER)
    (OUTPUT_DIR / "BUILD").write_text(BUILD_FILE)


def main() -> None:
    """
    Benchmarking a single Bazel target with a single source file. This is a large file using a lot of gtest macros.
    This benchmark ist focused at the performance of the preprocessing step to determine the included header files in the code under inspection.
    """
    create_test_setup()

    # Execute the Bazel commands from within the benchmarks workspace
    os.chdir(BENCHMARKS_DIR)

    primer = "//generated/complex_code:primer"
    target = "//generated/complex_code:benchmark"
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
