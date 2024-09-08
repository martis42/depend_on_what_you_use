# Semi automatic release process

## Release creation

1. `git tag VERSION`
1. `git push origin VERSION`
1. The CI will automatically create a draft PR
1. Check the release notes and fill manual sections
1. TODO do we have to set to 'pre-release', or can we continue with Draft for adding to BCR?

## Adding to BCR

1. Execute [scripts/deploy_to_bcr.py](/scripts/deploy_to_bcr.py) and provide version when asked for
1. Follow lnk in terminal and open PR on https://github.com/bazelbuild/bazel-central-registry

## Finish release

1. Wait until release is available via BCR
1. Make sure the release works via the [test repo](https://github.com/martis42/test_dwyu)
1. Finish release notes:
   - Remove BCR warning
   - Set to latest release
