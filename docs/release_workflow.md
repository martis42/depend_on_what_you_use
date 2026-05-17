# Release workflow

1. `git tag VERSION`
1. `git push origin VERSION`
1. The CI will automatically create a draft release and a draft PR for the BCR
   - Check the release notes and fill manual sections
   - Drop draft status on release and PR
1. Wait until release is available via the BCR
1. Make sure the release works via [test_release.py](/test/bcr_release/test_release.py)
1. Finish release notes:
   - Remove BCR warning
   - Set to latest release
