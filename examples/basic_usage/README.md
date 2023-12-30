Basic example showing correct and wrong dependency management and how DWYU reacts to those.

Executing DWYU on the correct target succeeds: <br>
`bazel build --aspects=//:aspect.bzl%dwyu --output_groups=dwyu //basic_usage:correct_dependencies`

Executing DWYU on the target with faulty dependency management <br>
`bazel build --aspects=//:aspect.bzl%dwyu --output_groups=dwyu //basic_usage:false_dependencies` <br>
yields a failed build and an error message outlining the two problems of this target.

Executing <br>
`bazel build --aspects=//:aspect.bzl%dwyu --output_groups=dwyu //basic_usage:not_using_lib` <br>
shows another error DWYU can find.
It reports that the target under inspection is depending on something, it is not even using.
