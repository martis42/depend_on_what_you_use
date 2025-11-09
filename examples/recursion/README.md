When invoking the DWYU aspect on a target pattern, it is by default executed solely on the specified targets.
In other words, pattern `//...` will execute DWYU on all targets in a workspace whereas `//foo:bar` will execute it on a single target.
Of course, one can also use more complex pattern or user bazel (c)query to compute a set of relevant targets.

For one common use case DWYU offers direct support: <br>
**_Executing DWYU on a target and all its transitive dependencies_**

Executing the following shows the default behavior which is a success, as the target under inspection has no fault.

```shell
bazel build --config=dwyu //recursion:use_lib
```

Executing the following fails however as it automatically analyzes the fault dependency used by the target under inspection.
See the [bazelrc](/examples/.bazelrc) file and [aspect.bzl](/examples/aspect.bzl) for the definition of the config and the aspect configuration.

```shell
bazel build --config=dwyu_recursive //recursion:use_lib
```
