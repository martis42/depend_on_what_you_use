#!/usr/bin/env python3

"""
We create a dedicated release archive instead of relying on in GitHubs builtin option because:
- It allows us to compute the checksum and automatically add it to the release notes
- Guarantees stable checksums
- Enables us to fetch metrics on the downloads

See also https://github.com/bazel-contrib/rules_oci/pull/62
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

from release_constants import BCR_PR_PLACEHOLDER

CHANGELOG = Path(__file__).resolve().parents[2] / "CHANGELOG.md"

CHANGES_TEMPLATE = """## Noteworthy Changes

{RELEASED_CHANGES}"""

RELEASE_NOTES_TEMPLATE = """{CHANGES}

## Using this release

:construction: **Deployment to BCR is not yet finished.** The release will be usable via bzlmod after this PR merged: {BCR_PR}

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


def extract_unreleased_changelog(changelog: Path = CHANGELOG) -> str:
    """
    Return the content between the '## Unreleased' headline and the first headline of an old release '## [version]'.
    """
    content: list[str] = []
    in_unreleased = False
    for line in changelog.read_text(encoding="utf-8").splitlines():
        if in_unreleased:
            if line.startswith("## ["):
                break
            content.append(line)
        elif line.strip() == "## Unreleased":
            in_unreleased = True
    return "\n".join(content).strip()


def parse_version(tag: str) -> tuple[int, ...] | None:
    if re.fullmatch(r"\d+\.\d+\.\d+", tag):
        return tuple(int(part) for part in tag.split("."))
    return None


def is_newest_release(tag: str) -> bool:
    """
    The 'Unreleased' changelog section only describes changes for the next release.
    Patching an old release must not copy those changes into the release notes.
    Thus, we only consider a tag for which no newer release tag exists.
    If we cannot reliably determine the existing tags, we defensively assume this is not the newest release.
    """
    version = parse_version(tag)
    if version is None:
        return False

    # In CI the checkout might contain only the tag being released
    fetch = subprocess.run(["git", "fetch", "--tags", "--quiet"], check=False, capture_output=True, text=True)
    if fetch.returncode != 0:
        print(f"ERROR: Could not fetch git tags: {fetch.stderr.strip()}", file=sys.stderr)  # noqa: T201
        return False
    tags = subprocess.run(["git", "tag", "--list"], check=True, capture_output=True, text=True).stdout.split()
    if tag not in tags:
        print(f"ERROR: Tag '{tag}' not found in the local repository", file=sys.stderr)  # noqa: T201
        return False

    existing_versions = [v for v in map(parse_version, tags) if v is not None]
    return all(existing <= version for existing in existing_versions)


def create_release_notes(tag: str, checksum: str, changelog: Path = CHANGELOG) -> str:
    to_be_released_changes = (
        extract_unreleased_changelog(changelog)
        if is_newest_release(tag)
        else "FAILED_TO_AUTOMATICALLY_ADD_RELEASED_CHANGES"
    )
    changes = CHANGES_TEMPLATE.format(RELEASED_CHANGES=to_be_released_changes) if to_be_released_changes else ""
    return RELEASE_NOTES_TEMPLATE.format(SHA=checksum, VERSION=tag, BCR_PR=BCR_PR_PLACEHOLDER, CHANGES=changes).strip()


def print_release_notes(archive: Path, tag: str) -> None:
    checksum_process = subprocess.run(["sha256sum", archive], check=True, capture_output=True, text=True)
    checksum = checksum_process.stdout.split(" ", 1)[0]
    print(create_release_notes(tag=tag, checksum=checksum))  # noqa: T201


if __name__ == "__main__":
    args = cli()
    release_artifact = make_archive(args.tag)
    print_release_notes(archive=release_artifact, tag=args.tag)
