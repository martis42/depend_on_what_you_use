from pathlib import Path
from time import time

from dwyu.aspect.private.analyze_includes.parse_source import extract_includes, fast_includes_extraction

# No benefit for using logging here
# ruff: noqa: T201


def run_test_fast_parsing(file: Path, step: int) -> float:
    print(f"\n### Start iteration {step}")
    start = time()
    fast_includes_extraction(file)
    duration = time() - start
    print(f"### Duration {duration:.3}")
    return duration


def run_test_correct_parsing(file: Path, defines: list[str], include_paths: list[str], step: int) -> float:
    print(f"\n### Start iteration {step}")
    start = time()
    extract_includes(
        file=file,
        defines=defines,
        include_paths=include_paths,
    )
    duration = time() - start
    print(f"### Duration {duration:.3}")
    return duration


def run_benchmark(file: Path, defines: list[str], include_paths: list[str], iterations: int) -> None:
    print("\n##")
    print("## Benchmark fast parsing")
    print("##")
    durations_fast = [run_test_fast_parsing(file=file, step=n + 1) for n in range(iterations)]

    print("\n##")
    print("## Benchmark correct parsing")
    print("##")
    durations_correct = [
        run_test_correct_parsing(file=file, defines=defines, include_paths=include_paths, step=n + 1)
        for n in range(iterations)
    ]

    print(f"\nAverage runtime fast parsing without preprocessor     : {sum(durations_fast) / len(durations_fast):.3}")
    print(
        f"Average runtime with correct parsing withpreprocessor : {sum(durations_correct) / len(durations_correct):.3}"
    )
