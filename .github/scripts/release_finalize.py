#!/usr/bin/env python3

"""
Finalize a release after its BCR deployment has been merged.

- Remove the warning about the BCR deployment not being finished from the release notes.
- Drop the prerelease status.
- Mark the release as latest, unless it is a patch for an old release.

Requires an authenticated GitHub CLI (GH_TOKEN) with write access to the contents of the release repository.
"""

import argparse
import logging
import sys

from release_constants import BCR_WARNING_END, BCR_WARNING_START
from release_github import find_bcr_pr, find_release, gh_api
from release_prep import is_newest_release

log = logging.getLogger(__name__)


def cli() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", required=True, help="Tag of the release to finalize")
    parser.add_argument("--repo", required=True, help="Repository hosting the release, e.g. 'owner/name'")
    return parser.parse_args()


def remove_bcr_warning(body: str) -> str:
    """
    Drop everything between the warning markers, including the markers and the blank line following them.
    Fail if the markers are not found exactly once and in the correct order, to never remove unrelated content.
    """
    lines = body.splitlines()
    starts = [i for i, line in enumerate(lines) if line.strip() == BCR_WARNING_START]
    ends = [i for i, line in enumerate(lines) if line.strip() == BCR_WARNING_END]
    if len(starts) != 1 or len(ends) != 1 or starts[0] > ends[0]:
        msg = f"Expected exactly one '{BCR_WARNING_START}' followed by one '{BCR_WARNING_END}' in the release notes"
        raise ValueError(msg)

    end = ends[0] + 1
    if end < len(lines) and not lines[end].strip():
        end += 1
    return "\n".join(lines[: starts[0]] + lines[end:])


def main() -> int:
    args = cli()
    release = find_release(args.repo, args.tag)

    if release["draft"]:
        log.error(f"Release {args.tag} is still a draft. Refusing to finalize.")
        return 1
    if not release["prerelease"]:
        log.info(f"Release {args.tag} is already finalized. Nothing to do.")
        return 0

    bcr_pr = find_bcr_pr(args.tag)
    if not bcr_pr.get("merged_at"):
        log.error(f"BCR PR {bcr_pr['html_url']} has not been merged. Refusing to finalize.")
        return 1

    try:
        new_body = remove_bcr_warning(release["body"] or "")
    except ValueError as error:
        log.error(f"{error}. Refusing to finalize, please adapt the release notes manually.")  # noqa: TRY400
        return 1

    make_latest = is_newest_release(args.tag)

    gh_api(
        f"repos/{args.repo}/releases/{release['id']}",
        "--method",
        "PATCH",
        "--field",
        f"body={new_body}",
        "--field",
        "prerelease=false",
        "--field",
        f"make_latest={str(make_latest).lower()}",
    )
    log.info(f"Finalized release {args.tag}. Marked as latest: {make_latest}")
    return 0


if __name__ == "__main__":
    logging.basicConfig(format="%(message)s", level=logging.INFO)
    sys.exit(main())
