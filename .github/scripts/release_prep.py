#!/usr/bin/env python3

"""
We create a dedicated release archive instead of relying on in GitHubs builtin option because:
- Guarantees stable checksums
- Enables us to fetch metrics on the downloads

See also https://github.com/bazel-contrib/rules_oci/pull/62
"""

import argparse
import logging
import subprocess
import sys
from pathlib import Path

from release_constants import BCR_PR_PLACEHOLDER, BCR_WARNING_END, BCR_WARNING_START

CHANGELOG = Path(__file__).resolve().parents[2] / "CHANGELOG.md"

CHANGES_TEMPLATE = """## Noteworthy Changes

{RELEASED_CHANGES}"""

RELEASE_NOTES_TEMPLATE = """{CHANGES}

## Using this release

{BCR_WARNING_START}
:construction: **Deployment to BCR is not yet finished.** The release will be usable via bzlmod after this PR merged: {BCR_PR}
{BCR_WARNING_END}

Add to your `MODULE.bazel` file:

```starlark
bazel_dep(name = "depend_on_what_you_use", version = "{VERSION}")
```

---
"""


def cli() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", metavar="VERSION", required=True, help="Tag for which to cut a release")
    return parser.parse_args()


def make_archive(tag: str) -> Path:
    """
    The prefix is the same as what GitHub generates for source archives.
    Thus, users can easily switch between the released archives and the source archives generated for each commit.
    """
    archive_format = "tar.gz"
    archive_prefix = f"depend_on_what_you_use-{tag}"
    archive = Path(f"depend_on_what_you_use-{tag}.{archive_format}")

    subprocess.run(
        ["git", "archive", f"--format={archive_format}", f"--prefix={archive_prefix}/", f"--output={archive}", tag],
        check=True,
    )

    return archive


def extract_release_changelog(tag: str, changelog: Path = CHANGELOG) -> str:
    """
    Return the content between the '## [tag]..' headline and the next release headline '## [previous_version]..'.
    If the changelog has no section for the tag, return an empty string.
    """
    content: list[str] = []
    in_release = False
    for line in changelog.read_text(encoding="utf-8").splitlines():
        if in_release:
            if line.startswith("## ["):
                break
            content.append(line)
        elif line.startswith(f"## [{tag}]"):
            in_release = True
    return "\n".join(content).strip()


def create_release_notes(tag: str, changelog: Path = CHANGELOG) -> str:
    released_changes = extract_release_changelog(tag, changelog)
    changes = CHANGES_TEMPLATE.format(RELEASED_CHANGES=released_changes) if released_changes else ""
    return RELEASE_NOTES_TEMPLATE.format(
        VERSION=tag,
        BCR_PR=BCR_PR_PLACEHOLDER,
        BCR_WARNING_START=BCR_WARNING_START,
        BCR_WARNING_END=BCR_WARNING_END,
        CHANGES=changes,
    ).strip()


if __name__ == "__main__":
    logging.basicConfig(format="%(message)s", level=logging.INFO)
    args = cli()
    make_archive(args.tag)
    sys.stdout.write(create_release_notes(tag=args.tag) + "\n")
