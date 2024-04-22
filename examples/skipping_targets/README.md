You might wish to not execute DWYU on some specific targets.
An easy way to do so is tagging a target with `no-dwyu`.
You can however also define a custom tag to mark targets which shall be skipped by the DWYU analysis.

Executing <br>
`bazel build --aspects=//:aspect.bzl%dwyu --output_groups=dwyu //skipping_targets:bad_target` <br>
fails due to the target using a header without a proper dependency.

Executing <br>
`bazel build --aspects=//:aspect.bzl%dwyu --output_groups=dwyu //skipping_targets:bad_target_skipped` <br>
succeeds due to the target being tagged with `no-dwyu`.

Executing <br>
`bazel build --aspects=//:aspect.bzl%dwyu_custom_skipping --output_groups=dwyu //skipping_targets:bad_target_custom_skip` <br>
showcases the same skipping behavior, but for the tag `mmy_tag` which we configured in [aspect.bzl](../aspect.bzl).

Executing <br>
`bazel build --aspects=//:aspect.bzl%dwyu_recursive_skip_external --output_groups=dwyu //skipping_targets:use_broken_external_dependency` <br>
showcases how we can ignore targets from external workspaces.
