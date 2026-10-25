"""Helpers for release automation scripts interacting with GitHub via an authenticated GitHub CLI (GH_TOKEN)."""

import json
import logging
import subprocess

from release_constants import BCR_FORK_OWNER, BCR_REPO, MODULE_NAME

log = logging.getLogger(__name__)


def setup_logging() -> None:
    logging.basicConfig(format="%(message)s", level=logging.INFO)


def gh_api(*args: str, payload: dict | None = None) -> str:
    """
    A payload is sent as JSON body, which keeps value types and content untouched.
    This is in contrast to the '--field' option, which interprets values like 'true', '@file' or '{owner}'.
    """
    try:
        return subprocess.run(
            ["gh", "api", *args, *(["--input", "-"] if payload is not None else [])],
            check=True,
            capture_output=True,
            text=True,
            input=json.dumps(payload) if payload is not None else None,
        ).stdout
    except subprocess.CalledProcessError as error:
        # The error message of the GitHub API is the only hint why a request was rejected
        log.error(f"'gh api {' '.join(args)}' failed:\n{error.stdout}\n{error.stderr}")  # noqa: TRY400
        raise


def update_release(repo: str, release_id: int, **fields: bool | str) -> None:
    gh_api(f"repos/{repo}/releases/{release_id}", "--method", "PATCH", payload=fields)


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
    # The API lists releases newest first
    page = 1
    while True:
        releases = json.loads(gh_api(f"repos/{repo}/releases?per_page=100&page={page}"))
        for release in releases:
            if release["tag_name"] == tag:
                return release
        if len(releases) < 100:
            break
        page += 1
    msg = f"No release found for tag '{tag}'"
    raise RuntimeError(msg)
