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
from release_github import setup_logging

log = logging.getLogger(__name__)

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
    Raise a ValueError if the changelog has no section for the tag or the section is empty.
    A release without documented changes must never be created unnoticed.
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

    if not in_release:
        msg = f"'{changelog}' has no section '## [{tag}]'"
        raise ValueError(msg)
    released_changes = "\n".join(content).strip()
    if not released_changes:
        msg = f"The section '## [{tag}]' in '{changelog}' is empty"
        raise ValueError(msg)
    return released_changes


def create_release_notes(tag: str, changelog: Path = CHANGELOG) -> str:
    return RELEASE_NOTES_TEMPLATE.format(
        VERSION=tag,
        BCR_PR=BCR_PR_PLACEHOLDER,
        BCR_WARNING_START=BCR_WARNING_START,
        BCR_WARNING_END=BCR_WARNING_END,
        CHANGES=CHANGES_TEMPLATE.format(RELEASED_CHANGES=extract_release_changelog(tag, changelog)),
    ).strip()


def main() -> int:
    args = cli()

    # Create the release notes first, so we fail before producing any release artifact
    try:
        release_notes = create_release_notes(tag=args.tag)
    except ValueError as error:
        log.error(f"{error}. Add the changes of this release to the changelog before tagging.")  # noqa: TRY400
        return 1

    make_archive(args.tag)
    sys.stdout.write(release_notes + "\n")
    return 0


if __name__ == "__main__":
    setup_logging()
    sys.exit(main())
