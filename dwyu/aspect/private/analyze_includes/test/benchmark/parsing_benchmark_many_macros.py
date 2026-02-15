#!/usr/bin/env python3


import os
import subprocess
import sys
from pathlib import Path
from shutil import rmtree

WS_DIR = os.getenv("BUILD_WORKING_DIRECTORY", None)
if not WS_DIR:
    # Not using Bazel to run the benchmark, thus manually set workspace root
    WS_DIR = subprocess.run(
        ["bazel", "--max_idle_secs=1", "info", "workspace"], check=True, shell=False, capture_output=True, text=True
    ).stdout.strip()

sys.path.append(WS_DIR)
OUTPUT_DIR = Path(WS_DIR) / "dwyu/aspect/private/analyze_includes/test/benchmark/parsing_examples/many_macros"

from dwyu.aspect.private.analyze_includes.test.benchmark.parsing_benchmark_lib import run_benchmark  # noqa: E402

TEST_FILE = OUTPUT_DIR / "foo.cpp"

TEST_CASES = 1000
NUM_DEFINES = 50
NUM_INCLUDE_PATHS = 50

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

BUILD_FILE = """
load("@rules_cc//cc:cc_test.bzl", "cc_test")

cc_test(
    name = "foo",
    srcs = ["foo.cpp"],
    tags = ["manual"],
    deps = [
        "@googletest//:gtest",
        "@googletest//:gtest_main",
    ],
)
""".lstrip()


def prepare_directory_layout() -> None:
    if OUTPUT_DIR.exists():
        rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True)


def create_files() -> None:
    tests = ""
    for n in range(TEST_CASES):
        tests += TEST_CASE.format(N=n)
    TEST_FILE.write_text(TEMPLATE.format(TESTS=tests))

    (OUTPUT_DIR / "BUILD").write_text(BUILD_FILE)

    # Ensure gtest was downlaoded
    subprocess.run(
        [
            "bazel",
            "--max_idle_secs=1",
            "build",
            "--nobuild",
            "//dwyu/aspect/private/analyze_includes/test/benchmark/parsing_examples/many_macros:all",
        ],
        cwd=WS_DIR,
        shell=False,
        check=True,
    )


def get_gtest_include_paths() -> list[str]:
    output_base = subprocess.run(
        ["bazel", "--max_idle_secs=1", "info", "output_base"],
        check=True,
        shell=False,
        cwd=WS_DIR,
        capture_output=True,
        text=True,
    ).stdout.strip()
    gtest_ext_dir = Path(output_base) / "external/googletest+"
    return [str(gtest_ext_dir / "googletest/include"), str(gtest_ext_dir / "googlemock/include")]


def get_system_include_paths() -> list[str]:
    return [
        "/usr/include",
        "/usr/include/c++/11",
        "/usr/include/linux",
        "/usr/include/x86_64-linux-gnu",
        "/usr/include/x86_64-linux-gnu/c++/11",
        "/usr/lib/gcc/x86_64-linux-gnu/11/include",
    ]


def main() -> None:
    """
    This benchmark requires access to include paths which are only valid for recent Bazel versions and a Linux host.
    Thus this benchmark is not partable.
    """
    prepare_directory_layout()
    create_files()

    defines = [f"SOME_DEFINE_{n}" for n in range(NUM_DEFINES)]
    defines.append("__cplusplus=201703")

    include_paths = [f"some/invlaid/include/path_{n}" for n in range(NUM_INCLUDE_PATHS)] + [".", str(OUTPUT_DIR)]
    include_paths.extend(get_gtest_include_paths())
    include_paths.extend(get_system_include_paths())

    # There is actually no major performance difference in the range 1 to 1'000 test macros in the test file. The main
    # probelm is parsing the complex gtest headers including their transitive inclusions. When having 10'000
    # test macros, the oparsing runtime increases significantly as then expanding the macros consumes the most time
    # during preprocessing.
    run_benchmark(file=TEST_FILE, defines=defines, include_paths=include_paths, iterations=5)


if __name__ == "__main__":
    main()
