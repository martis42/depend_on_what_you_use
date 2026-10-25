#!/usr/bin/env python3

"""
Insert the URL of the BCR pull request into the notes of the draft release.

The publish workflow creates the pull request, but the reusable upstream workflow does not expose its URL as output.
However, the PR head branch is deterministic (<module name>-<tag> in our registry fork).
Thus, we can look up the PR via the GitHub API.

Requires an authenticated GitHub CLI (GH_TOKEN) with write access to the contents of the release repository.
"""

import argparse
import json
import subprocess
import sys

# Must be identical to the placeholder in release_prep.py
BCR_PR_PLACEHOLDER = "BCR_PR_URL_PLACEHOLDER"

MODULE_NAME = "depend_on_what_you_use"
BCR_REPO = "bazelbuild/bazel-central-registry"
BCR_FORK_OWNER = "martis42"


def cli() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", required=True, help="Tag of the release to adapt")
    parser.add_argument("--repo", required=True, help="Repository hosting the release, e.g. 'owner/name'")
    return parser.parse_args()


def gh_api(*args: str) -> str:
    return subprocess.run(["gh", "api", *args], check=True, capture_output=True, text=True).stdout


def find_bcr_pr_url(tag: str) -> str:
    head = f"{BCR_FORK_OWNER}:{MODULE_NAME}-{tag}"
    pulls = json.loads(gh_api(f"repos/{BCR_REPO}/pulls?head={head}&state=all"))
    if not pulls:
        msg = f"No BCR pull request found for head '{head}'"
        raise RuntimeError(msg)
    return pulls[0]["html_url"]


def find_release(repo: str, tag: str) -> dict:
    # Draft releases are not accessible via their tag, thus we have to search the list of all releases
    release_ids = gh_api(
        f"repos/{repo}/releases", "--paginate", "--jq", f'.[] | select(.tag_name == "{tag}") | .id'
    ).split()
    if not release_ids:
        msg = f"No release found for tag '{tag}'"
        raise RuntimeError(msg)
    return json.loads(gh_api(f"repos/{repo}/releases/{release_ids[0]}"))


def main() -> int:
    args = cli()

    pr_url = find_bcr_pr_url(args.tag)
    release = find_release(args.repo, args.tag)

    # Fetch the body right before the update to minimize the risk of overwriting concurrent manual edits
    body = release["body"] or ""
    if BCR_PR_PLACEHOLDER not in body:
        print(f"Release notes contain no placeholder '{BCR_PR_PLACEHOLDER}'. Nothing to do. PR: {pr_url}")  # noqa: T201
        return 0

    gh_api(
        f"repos/{args.repo}/releases/{release['id']}",
        "--method",
        "PATCH",
        "--field",
        f"body={body.replace(BCR_PR_PLACEHOLDER, pr_url)}",
    )
    print(f"Added BCR PR {pr_url} to release notes of {args.tag}")  # noqa: T201
    return 0


if __name__ == "__main__":
    sys.exit(main())
