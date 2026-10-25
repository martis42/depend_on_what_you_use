#!/usr/bin/env python3

"""
Finalize a release after its BCR deployment has been merged.

- Remove the warning about the BCR deployment not being finished from the release notes.
- Drop the prerelease status.
- Mark the release as latest, unless it is a patch for an old release or this cannot be determined.

Requires an authenticated GitHub CLI (GH_TOKEN) with write access to the contents of the release repository.
"""

import argparse
import logging
import re
import subprocess
import sys

from release_constants import BCR_WARNING_END, BCR_WARNING_START
from release_github import find_bcr_pr, find_release, setup_logging, update_release

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


def parse_version(tag: str) -> tuple[int, ...] | None:
    if re.fullmatch(r"\d+\.\d+\.\d+", tag):
        return tuple(int(part) for part in tag.split("."))
    return None


def is_newest_release(tag: str) -> bool:
    """
    Return True if no release tag newer than the given tag exists.
    Patching an old release must not mark it as the latest release.
    If we cannot reliably determine the existing tags, we log a warning and return False.
    Not marking a release as latest is preferable to abandoning the whole finalization.
    """
    version = parse_version(tag)
    if version is None:
        log.warning(f"Tag '{tag}' is not a MAJOR.MINOR.PATCH version. Not marking the release as latest.")
        return False

    # In CI the checkout might contain only the tag being released
    fetch = subprocess.run(["git", "fetch", "--tags", "--quiet"], check=False, capture_output=True, text=True)
    if fetch.returncode != 0:
        log.warning(f"Could not fetch git tags: {fetch.stderr.strip()}. Not marking the release as latest.")
        return False
    tags = subprocess.run(["git", "tag", "--list"], check=True, capture_output=True, text=True).stdout.split()
    if tag not in tags:
        log.warning(f"Tag '{tag}' not found in the local repository. Not marking the release as latest.")
        return False

    existing_versions = [v for v in map(parse_version, tags) if v is not None]
    return all(existing <= version for existing in existing_versions)


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

    new_body = remove_bcr_warning(release["body"] or "")

    make_latest = is_newest_release(args.tag)

    # The API expects the string values 'true', 'false' or 'legacy' for 'make_latest'
    update_release(
        args.repo,
        release["id"],
        body=new_body,
        prerelease=False,
        make_latest=str(make_latest).lower(),
    )
    log.info(f"Finalized release {args.tag}. Marked as latest: {make_latest}")
    return 0


if __name__ == "__main__":
    setup_logging()
    sys.exit(main())
