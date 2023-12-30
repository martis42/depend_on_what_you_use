Your project might use headers for which a proper dependency is not possible.
One example for such a case would be a toolchain making headers beyond the C/C++ standard library globally available to your targets.

You can tell DWYU to ignore certain include statements to skip such headers for which a proper Bazel target dependency is not possible.

Executing <br>
`bazel build --aspects=//:aspect.bzl%dwyu_ignoring_includes --output_groups=dwyu //ignoring_includes:use_unavailable_headers` <br>
succeeds due to ignoring the include statements pointing to not existing headers as configured in [ignore_includes.json](./ignore_includes.json).
