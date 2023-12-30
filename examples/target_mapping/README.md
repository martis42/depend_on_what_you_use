You might not want to follow the DWYU design guidelines for all targets.
Maybe a public target acts as proxy for implementation detail targets which are providing the header files.
Or an external dependency outside your control is assumed to be used in a specific way.

To prevent DWYU from raising errors in such cases, we allow mapping the headers provided by the dependencies of a target to the target itself.

The targets in this example use headers from transitive dependencies.
Still, we can analyze them without DWYU raising an error when using an aspect configured with the corresponding target mapping.
You yee the mappings used in this example in [mapping](./mapping/BUILD).

Executing <br>
`bazel build --aspects=//:aspect.bzl%dwyu_map_specific_deps --output_groups=dwyu //target_mapping:use_lib_b` <br>
does not fail as we tell DWYU that library `a` provides the headers from library `b`.

Executing <br>
`bazel build --aspects=//:aspect.bzl%dwyu_map_direct_deps --output_groups=dwyu //target_mapping:use_lib_b` <br>
does not fail as we tell DWYU that library `a` provides the headers from all its direct dependencies and thus from library `b`.

DWYU still finds errors not covered by the provided mapping.
Executing <br>
`bazel build --aspects=//:aspect.bzl%dwyu_map_direct_deps --output_groups=dwyu //target_mapping:use_lib_c` <br>
fails due to library `c` being used but not being mapped to library `a`.

We can fix this problem easily with another target mapping.
Executing <br>
`bazel build --aspects=//:aspect.bzl%dwyu_map_transitive_deps --output_groups=dwyu //target_mapping:use_lib_c` <br>
succeeds as we tell DWYU to that library `a` provides the headers from all its transitive dependencies including library `c`.
