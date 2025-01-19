import os
import subprocess
from copy import deepcopy
from pathlib import Path
from shutil import which


def get_bazel_binary() -> Path:
    """
    We use bazelisk to control the exact Bazel version we test with. Using the native bazel binary would cause the tests
    to run with an arbitrary Bazel version without us noticing.
    """
    if bazel := which("bazelisk"):
        return Path(bazel)

    # Might be system where bazlisk was renamed to bazel or bazel links to a bazelisk binary not being on PATH.
    # We test this by using the '--strict' option which only exists for bazelisk, but not bazel
    bazel = which("bazel")
    if bazel and (
        subprocess.run([bazel, "--strict", "--version"], shell=False, check=False, capture_output=True).returncode == 0
    ):
        return Path(bazel)

    raise RuntimeError("No bazelisk binary or bazel symlink towards bazelisk available on your system")


def get_bazel_rolling_version(bazel_bin: Path) -> str:
    process = subprocess.run(
        [bazel_bin, "--version"],
        env=make_bazel_version_env("rolling"),
        shell=False,
        check=True,
        capture_output=True,
        text=True,
    )
    return process.stdout.split("bazel")[1].strip()


def make_bazel_version_env(version: str) -> os._Environ:
    run_env = deepcopy(os.environ)
    run_env["USE_BAZEL_VERSION"] = version
    return run_env


def get_current_workspace(bazel_bin: Path) -> Path:
    cmd = [
        str(bazel_bin),
        # Make sure no idle server lives forever wasting RAM
        "--max_idle_secs=10",
        "info",
        "workspace",
    ]
    process = subprocess.run(cmd, shell=False, check=True, capture_output=True, text=True)
    return Path(process.stdout.strip())
