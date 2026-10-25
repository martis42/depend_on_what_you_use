#!/usr/bin/env python3

"""
Mark the BCR deployment pull request as "ready for review".

The BCR does not allow PR authors to approve their own PRs and our PR is authored by the owner of the BCR_PUBLISH_TOKEN, who is a maintainer of the module.
The BCR PR reviewer bot (https://github.com/bazelbuild/continuous-integration/tree/master/actions/bcr-pr-reviewer) counts a maintainer as approved if they authored the PR.
It skips draft PRs, which makes leaving the draft state the signal that the release should be merged.
The bot does not check who removed the draft state.

Requires an authenticated GitHub CLI (GH_TOKEN) with write access to the BCR pull request, i.e. the BCR_PUBLISH_TOKEN.
The default GitHub Actions token cannot be used, since it has no permissions for the BCR repository.
"""

import argparse
import logging
import subprocess
import sys

from release_github import find_bcr_pr, setup_logging

log = logging.getLogger(__name__)


def cli() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", required=True, help="Tag of the release whose BCR deployment is made ready")
    return parser.parse_args()


def main() -> int:
    args = cli()
    pr = find_bcr_pr(args.tag)

    if pr["state"] != "open":
        if pr.get("merged_at"):
            log.info(f"BCR PR {pr['html_url']} has already been merged. Nothing to do.")
            return 0
        log.error(f"BCR PR {pr['html_url']} was closed without being merged. Please investigate and republish.")
        return 1
    if not pr["draft"]:
        log.info(f"BCR PR {pr['html_url']} is already ready for review. Nothing to do.")
        return 0

    subprocess.run(["gh", "pr", "ready", pr["html_url"]], check=True)
    log.info(f"Marked BCR PR {pr['html_url']} as ready for review")
    return 0


if __name__ == "__main__":
    setup_logging()
    sys.exit(main())
