import subprocess
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
