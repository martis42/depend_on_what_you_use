"""Helpers for release automation scripts interacting with GitHub via an authenticated GitHub CLI (GH_TOKEN)."""

import json
import subprocess

from release_constants import BCR_FORK_OWNER, BCR_REPO, MODULE_NAME

RELEASES_PAGE_SIZE = 10


def gh_api(*args: str) -> str:
    return subprocess.run(["gh", "api", *args], check=True, capture_output=True, text=True).stdout


def find_bcr_pr(tag: str) -> dict:
    # The publish workflow uses a deterministic head branch in our registry fork
    head = f"{BCR_FORK_OWNER}:{MODULE_NAME}-{tag}"
    pulls = json.loads(gh_api(f"repos/{BCR_REPO}/pulls?head={head}&state=all"))
    if not pulls:
        msg = f"No BCR pull request found for head '{head}'"
        raise RuntimeError(msg)
    return pulls[0]


def find_release(repo: str, tag: str) -> dict:
    # Draft releases are not accessible via their tag, thus we have to search the list of all releases
    # The API lists releases newest first. We usually look for a just created release, so small pages suffice.
    page = 1
    while True:
        releases = json.loads(gh_api(f"repos/{repo}/releases?per_page={RELEASES_PAGE_SIZE}&page={page}"))
        for release in releases:
            if release["tag_name"] == tag:
                return release
        if len(releases) < RELEASES_PAGE_SIZE:
            break
        page += 1
    msg = f"No release found for tag '{tag}'"
    raise RuntimeError(msg)
