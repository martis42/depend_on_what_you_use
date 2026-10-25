"""Helpers for release automation scripts interacting with GitHub via an authenticated GitHub CLI (GH_TOKEN)."""

import json
import subprocess

from release_constants import BCR_FORK_OWNER, BCR_REPO, MODULE_NAME


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
    release_ids = gh_api(
        f"repos/{repo}/releases", "--paginate", "--jq", f'.[] | select(.tag_name == "{tag}") | .id'
    ).split()
    if not release_ids:
        msg = f"No release found for tag '{tag}'"
        raise RuntimeError(msg)
    return json.loads(gh_api(f"repos/{repo}/releases/{release_ids[0]}"))
