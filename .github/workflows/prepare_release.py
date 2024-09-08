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
## Using Bzlmod (Recommended)

> :construction: Not yet deployed to BCR :construction:
> Release will become usable via bzlmod as soon as it is no longer the pre-release phase.

Add to your `MODULE.bazel` file:

```starlark
bazel_dep(name = "depend_on_what_you_use", version = "{VERSION}")
```

## Using WORKSPACE (Legacy)

Add to your `WORKSPACE` file:

```starlark
load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

http_archive(
    name = "depend_on_what_you_use",
    sha256 = "{SHA}",
    strip_prefix = "depend_on_what_you_use-{VERSION}",
    url = "https://github.com/martis42/depend_on_what_you_use/releases/download/{VERSION}/depend_on_what_you_use-{VERSION}.tar.gz",
)

load("@depend_on_what_you_use//:setup_step_1.bzl", dwyu_setup_step_1 = "setup_step_1")
dwyu_setup_step_1()

load("@depend_on_what_you_use//:setup_step_2.bzl", dwyu_setup_step_2 = "setup_step_2")
dwyu_setup_step_2()
```

## Breaking Changes

TBD

## Noteworthy Changes

TBD

---
"""


def cli() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", metavar="VERSION", help="Tag for which to cut a release")
    return parser.parse_args()


def make_archive(tag: str) -> Path:
    """
    The prefix is the same as what GitHub generates for source archives.
    Thus, users cans easily switch between the released archives and the source archives generated for reach commit.

    We can filter out some files via a .gitignore file. see:
    https://github.com/bazel-contrib/rules-template/blob/4e541c8083645da37eb570c23e04dc65e1d6446c/.gitattributes
    We use this filtering sparsely to ensure our released artifact is compatible to the archives generated by GitHub
    when users reference a specific commit as outlined in our README.
    """
    archive_format = "tar.gz"
    archive_prefix = f"depend_on_what_you_use-{tag}"
    archive = Path(f"depend_on_what_you_use-{tag}.{archive_format}")

    subprocess.run(
        ["git", "archive", f"--format={archive_format}", f"--prefix={archive_prefix}/", f"--output={archive}", tag],
        check=True,
    )

    return archive


def make_release_notes(archive: Path, tag: str) -> None:
    checksum_process = subprocess.run(["sha256sum", archive], check=True, capture_output=True, text=True)
    checksum = checksum_process.stdout.split(" ", 1)[0]
    with Path("release_notes.txt").open(mode="w", encoding="utf-8") as release_notes:
        release_notes.write(RELEASE_NOTES_TEMPLATE.format(SHA=checksum, VERSION=tag).strip())


if __name__ == "__main__":
    args = cli()
    release_artifact = make_archive(args.tag)
    make_release_notes(archive=release_artifact, tag=args.tag)
