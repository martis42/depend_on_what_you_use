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

LIB_FILES = 250
CLASSES_PER_FILE = 75

ITERATIONS = 3
JOBS = 1

#
# Generation templates
#

BENCHMARKS_DIR = WS_ROOT / "test/benchmark"
OUTPUT_DIR = BENCHMARKS_DIR / "generated/many_files"
LIB_DIR = OUTPUT_DIR / "lib"

CORE_LIB_HEADER = """
#ifndef CORE_LIB_HEADER_H
#define CORE_LIB_HEADER_H

#include <cstdint>

namespace test {

struct ByteMover {
    ByteMover() = default;
    virtual ~ByteMover() = default;

    virtual void MoveBytes() = 0;

    std::int32_t magic_parameter_{42};
};

}

#endif
"""

DUMMY_CLASS = """
class ByteMover_{N} : public test::ByteMover {{
  public:
    ByteMover_{N}() : test::ByteMover{{}} {{
        b_.resize(1337);
        std::fill(b_.begin(), b_.end(), 42);
    }}

    void MoveBytes() override {{
        std::partition(b_.begin(), b_.end(), [](std::int32_t i) {{return i % 2 == 0;}});
        std::sort(b_.begin(), b_.end());
        const auto [min, max] = std::minmax_element(b_.begin(), b_.end());
        std::cout << *min << " - " << *max;
    }}

  private:
    std::vector<std::int32_t> b_;
}};
"""

LIB_HEADER_TEMPLATE = """
#ifndef LIB_HEADER_{N}_H
#define LIB_HEADER_{N}_H

#include "core_lib_header.h"

#include <algorithm>
#include <cstdint>
#include <iostream>
#include <vector>

namespace test_{N} {{

{CONTENT}

}}

#endif
"""

LIB_IMPL = """
#include "lib/core_lib_header.h"

{INCLUDES}

#include <memory>
#include <vector>

namespace foo {{

void MoveStuff() {{
    std::vector<std::shared_ptr<test::ByteMover>> movers;

{MOVERS}

    for(auto& m : movers) {{
        m->MoveBytes();
    }}
}}

}}

int main() {{
    foo::MoveStuff();
    return 0;
}}
"""

PRIMER = "void SomeFn() {}"

BUILD_FILE = """
load("@rules_cc//cc:cc_binary.bzl", "cc_binary")
load("@rules_cc//cc:cc_library.bzl", "cc_library")

cc_binary(
    name = "benchmark",
    srcs = ["main.cpp"] + glob(["lib/*.h"]),
)

cc_library(
    name = "primer",
    srcs = ["primer.cpp"],
)
""".lstrip()


def prepare_directory_layout() -> None:
    if OUTPUT_DIR.exists():
        rmtree(OUTPUT_DIR)
    LIB_DIR.mkdir(parents=True)


def create_test_setup() -> None:
    prepare_directory_layout()

    (LIB_DIR / "core_lib_header.h").write_text(CORE_LIB_HEADER)

    for n in range(LIB_FILES):
        content = ""
        for d in range(CLASSES_PER_FILE):
            content += DUMMY_CLASS.format(N=f"{n}_{d}")
            content += "\n"
        (LIB_DIR / f"lib_header_{n}.h").write_text(LIB_HEADER_TEMPLATE.format(N=n, CONTENT=content))

    includes = "\n".join(f'#include "lib/lib_header_{n}.h"' for n in range(LIB_FILES))
    movers = "\n".join(
        f"    movers.push_back(std::make_shared<test_{n}::ByteMover_{n}_{d}>());"
        for n in range(LIB_FILES)
        for d in range(CLASSES_PER_FILE)
    )
    (OUTPUT_DIR / "main.cpp").write_text(LIB_IMPL.format(INCLUDES=includes, MOVERS=movers))

    (OUTPUT_DIR / "primer.cpp").write_text(PRIMER)
    (OUTPUT_DIR / "BUILD").write_text(BUILD_FILE)


def main() -> None:
    """
    Benchmarking a single Bazel target with many large files with a lot of code. The main files includes all other files directly.
    The focus of this benchmark are targets with many source files and many include statements.
    The demand on the preprocessing step is mediocre. There is much code, but it is easy to parse.
    """
    create_test_setup()

    # Execute the Bazel commands from within the benchmarks workspace
    os.chdir(BENCHMARKS_DIR)

    primer = "//generated/many_files:primer"
    target = "//generated/many_files:benchmark"
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
