#!/usr/bin/env python3

"""
We create a dedicated release archive instead of relying on in GitHubs builtin option because:
- It allows us to compute the checksum and automatically add it to the release notes
- Guarantees stable checksums
- Enables us to fetch metrics on the downloads

See also https://github.com/bazel-contrib/rules_oci/pull/62
"""

import argparse
import subprocess
from pathlib import Path

RELEASE_NOTES_TEMPLATE = """
TBD summary

## Noteworthy Changes

### Changed

TBD - Mark what is breaking !

### Fixed

TBD

### Added

TBD

## Using this release

:construction: **Deployment to BCR is not yet finished.** The release will be usable via bzlmod after this PR merged: TBD

Add to your `MODULE.bazel` file:

```starlark
bazel_dep(name = "depend_on_what_you_use", version = "{VERSION}")
```

---
"""


def cli() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", metavar="VERSION", help="Tag for which to cut a release")
    return parser.parse_args()


def make_archive(tag: str) -> Path:
    """
    The prefix is the same as what GitHub generates for source archives.
    Thus, users can easily switch between the released archives and the source archives generated for reach commit.
    To minimize the release size, we filter out development only content via the .gitattributes file.
    """
    archive_format = "tar.gz"
    archive_prefix = f"depend_on_what_you_use-{tag}"
    archive = Path(f"depend_on_what_you_use-{tag}.{archive_format}")

    subprocess.run(
        ["git", "archive", f"--format={archive_format}", f"--prefix={archive_prefix}/", f"--output={archive}", tag],
        check=True,
    )

    return archive


def print_release_notes(archive: Path, tag: str) -> None:
    checksum_process = subprocess.run(["sha256sum", archive], check=True, capture_output=True, text=True)
    checksum = checksum_process.stdout.split(" ", 1)[0]
    print(RELEASE_NOTES_TEMPLATE.format(SHA=checksum, VERSION=tag).strip())  # noqa: T201


if __name__ == "__main__":
    args = cli()
    release_artifact = make_archive(args.tag)
    print_release_notes(archive=release_artifact, tag=args.tag)
