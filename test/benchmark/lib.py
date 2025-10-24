from __future__ import annotations

import argparse
import logging
import shlex
import subprocess
from statistics import stdev
from time import time

log = logging.getLogger()


def common_main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", "-v", action="store_true", help="Show debugging information")

    args = parser.parse_args()
    if args.verbose:
        log.setLevel(logging.DEBUG)


def run_benchmark(aspect: str, primer: str, bench_target: str, description: str, iterations: int, jobs: int) -> None:
    capture_output = not log.isEnabledFor(logging.DEBUG)
    option_jobs = [f"--jobs={jobs}"] if jobs > 0 else []
    cmd_base = [
        "bazel",
        "build",
        # Be sure not be unfair in Python vs precompiled tools
        "--nolegacy_external_runfiles",
        # We do not care about those warnings while benchmarking
        "--check_direct_dependencies=off",
        "--output_groups=dwyu",
    ]
    cmd_dwyu = [*cmd_base, f"--aspects=//:aspect.bzl%{aspect}"]

    log.info(f"\n#### Running Benchmark - {description}\n")
    times = []
    log.debug(f"Benchmarking cmd: {shlex.join(cmd_dwyu)}\n")
    for n in range(1, iterations + 1):
        log.info(f"\n>> Iteration {n}")

        # Make sure no cached results are used
        subprocess.run(["bazel", "clean"], shell=False, check=True, capture_output=capture_output)

        # Ensure all tools are prebuilt and Bazel server is ready
        subprocess.run([*cmd_dwyu, "--", primer], shell=False, check=True, capture_output=capture_output)

        # Run benchmark command
        start = time()
        subprocess.run(
            [*cmd_dwyu, *option_jobs, "--", bench_target], shell=False, check=True, capture_output=capture_output
        )
        duration = time() - start
        times.append(duration)
        log.info(f">> Duration {duration:.3f} [s]")

    log.info("\nSummary")
    average_time = sum(times) / len(times)
    log.info(f"  Minimum runtime    : {min(times):.3f} [s]")
    if len(times) > 1:
        log.info(f"  Average runtime    : {average_time:.3f} [s]")
        log.info(f"  Standard deviation : {stdev(times):.3f} [s]")
    log.info("")
