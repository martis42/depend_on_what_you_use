#!/usr/bin/env python3

"""
Publish the draft release, but keep it marked as prerelease.

The prerelease status is our marker for the BCR deployment not being finished yet.
Publishing the release is required before the BCR deployment pull request can be processed, since the BCR needs to download the release artifacts.

Requires an authenticated GitHub CLI (GH_TOKEN) with write access to the contents of the release repository.
"""

import argparse
import logging
import sys

from release_constants import BCR_PR_PLACEHOLDER
from release_github import find_release, setup_logging, update_release

log = logging.getLogger(__name__)


def cli() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", required=True, help="Tag of the release to publish")
    parser.add_argument("--repo", required=True, help="Repository hosting the release, e.g. 'owner/name'")
    return parser.parse_args()


def main() -> int:
    args = cli()
    release = find_release(args.repo, args.tag)

    if not release["draft"]:
        log.info(f"Release {args.tag} is already published. Nothing to do.")
        return 0

    # Problems in the release notes are easy to fix manually later and no automated step depends on them
    if BCR_PR_PLACEHOLDER in (release["body"] or ""):
        log.warning(f"Release notes of {args.tag} still contain '{BCR_PR_PLACEHOLDER}'. Please fix this manually.")

    update_release(args.repo, release["id"], draft=False, prerelease=True)
    log.info(f"Published release {args.tag} as prerelease")
    return 0


if __name__ == "__main__":
    setup_logging()
    sys.exit(main())
