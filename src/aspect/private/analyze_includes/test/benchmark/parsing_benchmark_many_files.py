#!/usr/bin/env python3
from __future__ import annotations

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
OUTPUT_DIR = Path(WS_DIR) / "src/aspect/private/analyze_includes/test/benchmark/parsing_examples/many_files"

from src.aspect.private.analyze_includes.test.benchmark.parsing_benchmark_lib import run_benchmark  # noqa: E402

LIB_DIR = OUTPUT_DIR / "lib"
MAIN = OUTPUT_DIR / "main.cpp"

LIB_FILES = 100
DUMMY_CLASSES_PER_FILE = 100
NUM_DEFINES = 50
NUM_INCLUDE_PATHS = 50

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

#endif // CORE_LIB_HEADER_H
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

#include "lib/core_lib_header.h"

#include <algorithm>
#include <cstdint>
#include <iostream>
#include <vector>

namespace test_{N} {{

{CONTENT}

}}

#endif // LIB_HEADER_{N}_H
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

BUILD_FILE = """
load("@rules_cc//cc:cc_binary.bzl", "cc_binary")

cc_binary(
    name = "foo",
    srcs = ["main.cpp"] + glob(["lib/*.h"]),
    tags = ["manual"],
)
""".lstrip()


def prepare_directory_layout() -> None:
    if OUTPUT_DIR.exists():
        rmtree(OUTPUT_DIR)
    LIB_DIR.mkdir(parents=True)


def create_files() -> None:
    (LIB_DIR / "core_lib_header.h").write_text(CORE_LIB_HEADER)

    for n in range(LIB_FILES):
        content = ""
        for d in range(DUMMY_CLASSES_PER_FILE):
            content += DUMMY_CLASS.format(N=f"{n}_{d}")
            content += "\n"
        (LIB_DIR / f"lib_header_{n}.h").write_text(LIB_HEADER_TEMPLATE.format(N=n, CONTENT=content))

    includes = "\n".join(f'#include "lib/lib_header_{n}.h"' for n in range(LIB_FILES))
    movers = "\n".join(
        f"    movers.push_back(std::make_shared<test_{n}::ByteMover_{n}_{d}>());"
        for n in range(LIB_FILES)
        for d in range(DUMMY_CLASSES_PER_FILE)
    )
    MAIN.write_text(LIB_IMPL.format(INCLUDES=includes, MOVERS=movers))

    (OUTPUT_DIR / "BUILD").write_text(BUILD_FILE)


def main() -> None:
    prepare_directory_layout()
    create_files()

    defines = [f"SOME_DEFINE_{n}" for n in range(NUM_DEFINES)]

    include_paths = [f"some/invlaid/include/path_{n}" for n in range(NUM_INCLUDE_PATHS)]
    include_paths.append(str(OUTPUT_DIR))

    run_benchmark(file=MAIN, defines=defines, include_paths=include_paths, iterations=5)


if __name__ == "__main__":
    main()
