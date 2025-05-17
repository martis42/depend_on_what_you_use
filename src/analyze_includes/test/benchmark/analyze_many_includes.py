import time
from pathlib import Path

from src.analyze_includes.evaluate_includes import evaluate_includes
from src.analyze_includes.parse_source import Include
from src.analyze_includes.system_under_inspection import CcTarget, SystemUnderInspection

INCLUDES = 250
FILES_PER_TARGET = 250
DEPS = 250
INCLUDE_PATHS = 100

# No benefit for using logging here
# ruff: noqa: T201


def main() -> None:
    # Set up a situation with many invalid includes. This is the worst case scenario for the runtime of the analysis.
    system = SystemUnderInspection(
        target_under_inspection=CcTarget(
            name="main_target", header_files=[f"main/target/file_{f}.h" for f in range(FILES_PER_TARGET)]
        ),
        deps=[
            CcTarget(name=f"dep_{d}", header_files=[f"some/dep_{d}/file_{f}.h" for f in range(FILES_PER_TARGET)])
            for d in range(DEPS)
        ],
        impl_deps=[
            CcTarget(
                name=f"impl_dep_{d}", header_files=[f"some/impl_dep_{d}/file_{f}.h" for f in range(FILES_PER_TARGET)]
            )
            for d in range(DEPS)
        ],
        include_paths=[f"some/include/path/{ip}" for ip in range(INCLUDE_PATHS)],
        defines=[""],  # irrelevant for analyzing includes, which happens after parsing
    )

    public_includes = [
        Include(
            file=Path(f"some/public/random/file_{i}.h"), include=f"wrong/public/include/statement/to/non_existing_{i}.h"
        )
        for i in range(INCLUDES)
    ]
    private_includes = [
        Include(
            file=Path(f"some/private/random/file_{i}.h"),
            include=f"wrong/private/include/statement/to/non_existing_{i}.h",
        )
        for i in range(INCLUDES)
    ]

    start = time.time()
    evaluate_includes(
        public_includes=public_includes,
        private_includes=private_includes,
        system_under_inspection=system,
        ensure_private_deps=True,
    )
    end = time.time()
    print("\nDuration: ", end - start)


if __name__ == "__main__":
    main()
