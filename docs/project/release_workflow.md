# Release workflow

This document describes how maintainers publish a DWYU release.
For the user-facing compatibility and versioning policy, see [Versioning](/README.md#versioning) and the [changelog](/CHANGELOG.md).

**Note**: We are using the `prerelease` status as marker for a release being _work in progress_.
The deployment to the Bazel central registry (BCR) takes some time or can fail due to reasons invisible to our own CI
After a release has been finished, we drop the `prerelease` status.

## Create and validate the release

1. [Manual] Choose a version:
   - Follow the project's [SemVer interpretation](/README.md#versioning).
   - Prepare the release by adding a section for the release to the [changelog](/CHANGELOG.md).
1. [Manual] After the changelog preparation PR merged, create and push a tag matching `MAJOR.MINOR.PATCH`, without a `v` prefix.
   For example:
   - `git tag 1.2.3`
   - `git push origin 1.2.3`
1. [Automatic] On pushing a tag the CI starts the [release workflow](/.github/workflows/release.yaml):
   - Run the check jobs again as final verification.
   - Create a draft release.
   - Open a draft PR for deploying the release to the [BCR](https://github.com/bazelbuild/bazel-central-registry).
   - Add a link to the BCR deployment draft PR into the release notes.
   - Publish the GitHub release by removing its draft status, but keep it marked as a **prerelease**.
   - Make the BCR deployment draft PR _ready for review_, which triggers its merge once the BCR checks pass.
1. [Manual] Wait until the BCR deployment PR has been merged and then trigger the [finalize release workflow](/.github/workflows/release_finalize.yaml) from the GitHub Actions web page and enter the version being released.
   This will:
   - Verify the release is indeed consumable via bzlmod by running the [release smoke test](/test/bcr_release/test_release.py).
   - Remove the warning about the BCR deployment not yet being done from the release notes.
   - Drop the prerelease status.
   - Mark it as latest release, unless this was a patch for an old release.
