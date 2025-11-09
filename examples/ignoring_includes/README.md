Your project might use headers for which a proper dependency is not possible.
One example for such a case would be a toolchain making headers beyond the C/C++ standard library globally available to your targets.

You can tell DWYU to ignore certain include statements to skip such headers for which a proper Bazel target dependency is not possible.

Executing the following succeeds due to ignoring the include statements pointing to not existing headers as configured in [ignore_includes.json](./ignore_includes.json).
See the [bazelrc](/examples/.bazelrc) file and [aspect.bzl](/examples/aspect.bzl) for the definition of the config and the aspect configuration.

```shell
bazel build --config=dwyu_ignoring_includes //ignoring_includes:use_unavailable_headers
```
