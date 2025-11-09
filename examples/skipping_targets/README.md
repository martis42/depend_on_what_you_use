You might wish to not execute DWYU on some specific targets.
An easy way to do so is tagging a target with `no-dwyu`.
You can however also define a custom tag to mark targets which shall be skipped by the DWYU analysis.

Executing the following fails due to the target using a header without a proper dependency.

```shell
bazel build --config=dwyu //skipping_targets:bad_target
```

Executing the following succeeds due to the target being tagged with `no-dwyu`.

```shell
bazel build --config=dwyu //skipping_targets:bad_target_skipped
```

Executing the following showcases the same skipping behavior, but for the tag `mmy_tag`.
See the [bazelrc](/examples/.bazelrc) file and [aspect.bzl](/examples/aspect.bzl) for the definition of the config and the aspect configuration.

```shell
bazel build --config=dwyu_custom_skipping //skipping_targets:bad_target_custom_skip
```

Executing the following showcases how we can ignore targets from external workspaces.
See the [bazelrc](/examples/.bazelrc) file and [aspect.bzl](/examples/aspect.bzl) for the definition of the config and the aspect configuration.

```shell
bazel build --config=dwyu_skip_external //skipping_targets:use_broken_external_dependency
```
