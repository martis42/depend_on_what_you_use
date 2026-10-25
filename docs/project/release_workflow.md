# Release workflow

This document describes how maintainers publish a DWYU release.
For the user-facing compatibility and versioning policy, see [Versioning](/README.md#versioning) and the [changelog](/CHANGELOG.md).

**Note**: We are using the `prerelease` status as marker for a release being _work in progress_.
The deployment to the Bazel central registry (BCR) takes some time or can fail due to reasons invisible to our own CI
After a release has been finished, we drop the `prerelease` status.

## Create and validate the release

1. [Manual] Choose a version:
   - Follow the project's [SemVer interpretation](/README.md#versioning).
   - Ensure the Changelog has been maintained since the last release.
   - Ensure the last CI run passed.
1. [Manual] Create and push a tag matching `MAJOR.MINOR.PATCH`, without a `v` prefix.
   For example:
   - `git tag 1.2.3`
   - `git push origin 1.2.3`
1. [Automatic] On pushing a tag the CI starts the [release workflow](/.github/workflows/release.yaml):
   - Run the check jobs again as final verification.
   - Create a draft release.
   - Open a draft PR for deploying the release to the [BCR](https://github.com/bazelbuild/bazel-central-registry).
   - Add a link to the BCR deployment draft PR into the release notes.
1. [Manual] Check release notes.
   Did the automatic changelog extraction work?
   In case of a patch to an old release, the released changes have to be added manually.
1. [Manual] Trigger the deployment
   - Publish the GitHub release by removing its draft status, but keep it marked as a **prerelease**.
   - Make the BCR deployment draft PR _ready for review_.
1. [Manual] Wait until the BCR deployment PR has been merged
1. [Manual] Verify the release is indeed consumable via bzlmod by running the [release smoke test](/test/bcr_release/test_release.py) and entering the version being released when prompted.
1. [Manual] Finalize the release:
   - Remove the warning about the BCR deployment not yet being done
   - Drop the prerelease status
   - Mark it as latest release, unless this was a patch for an old release.
1. [Manual] Update Changelog to release.
   All formerly unreleased parts which have been copied into the release notes should be below a headline for the new release.
