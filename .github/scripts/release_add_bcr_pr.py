#!/usr/bin/env python3

"""
Insert the URL of the BCR pull request into the notes of the draft release.

The publish workflow creates the pull request, but the reusable upstream workflow does not expose its URL as output.
However, the PR head branch is deterministic (<module name>-<tag> in our registry fork).
Thus, we can look up the PR via the GitHub API.

Requires an authenticated GitHub CLI (GH_TOKEN) with write access to the contents of the release repository.
"""

import argparse
import logging
import sys

from release_constants import BCR_PR_PLACEHOLDER
from release_github import find_bcr_pr, find_release, setup_logging, update_release

log = logging.getLogger(__name__)


def cli() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", required=True, help="Tag of the release to adapt")
    parser.add_argument("--repo", required=True, help="Repository hosting the release, e.g. 'owner/name'")
    return parser.parse_args()


def main() -> int:
    args = cli()

    pr_url = find_bcr_pr(args.tag)["html_url"]
    release = find_release(args.repo, args.tag)

    # Fetch the body right before the update to minimize the risk of overwriting concurrent manual edits
    body = release["body"] or ""
    if BCR_PR_PLACEHOLDER not in body:
        log.info(f"Release notes contain no placeholder '{BCR_PR_PLACEHOLDER}'. Nothing to do. PR: {pr_url}")
        return 0

    update_release(args.repo, release["id"], body=body.replace(BCR_PR_PLACEHOLDER, pr_url))
    log.info(f"Added BCR PR {pr_url} to release notes of {args.tag}")
    return 0


if __name__ == "__main__":
    setup_logging()
    sys.exit(main())
