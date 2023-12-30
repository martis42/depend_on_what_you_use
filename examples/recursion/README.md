When invoking the DWYU aspect on a target pattern, it is by default executed solely on the specified targets.
In other words, pattern `//...` will execute DWYU on all targets in a workspace whereas `//foo:bar` will execute it on a single target.
Of course, one can also use more complex pattern or user bazel (c)query to compute a set of relevant targets.

For one common use case DWYU offers direct support: <br>
**_Executing DWYU on a target and all its transitive dependencies_**

Executing <br>
`bazel build --aspects=//:aspect.bzl%dwyu --output_groups=dwyu //recursion:use_lib` <br>
shows the default behavior which is a success, as the target under inspection has no fault.

Executing <br>
`bazel build --aspects=//:aspect.bzl%dwyu_recursive --output_groups=dwyu //recursion:use_lib` <br>
fails however as it automatically analyzes the fault dependency used by the target under inspection.
