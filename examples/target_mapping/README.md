You might not want to follow the DWYU design guidelines for all targets.
Maybe a public target acts as proxy for implementation detail targets which are providing the header files.
Or an external dependency outside your control is assumed to be used in a specific way.

To prevent DWYU from raising errors in such cases, we allow mapping the headers provided by the dependencies of a target to the target itself.

The targets in this example use headers from transitive dependencies.
Still, we can analyze them without DWYU raising an error when using an aspect configured with the corresponding target mapping.
You yee the mappings used in this example in [mapping](./mapping/BUILD).

See the [bazelrc](/examples/.bazelrc) file and [aspect.bzl](/examples/aspect.bzl) for the definition of the configs and the aspect configurations.

Executing the following does not fail as we explicitly map library `b` to `a`, telling DWYU that `a` provides the headers from `b`.

```shell
bazel build --config=dwyu_map_specific_deps //target_mapping:use_lib_b
```

Executing the following does not fail as we tell DWYU that library `a` provides the headers from all its direct dependencies and thus from library `b`.

```shell
bazel build --config=dwyu_map_direct_deps //target_mapping:use_lib_b
```

DWYU can still discover errors not covered by the provided mapping.
Executing the following fails due to library `c` being used but not being mapped to library `a`.

```shell
bazel build --config=dwyu_map_direct_deps //target_mapping:use_lib_c
```

We can fix this problem easily with another kind of target mapping.
Executing the following succeeds as we tell DWYU to that library `a` provides the headers from dependency `b` including all its transitive dependencies including library `c`.

```shell
bazel build --config=dwyu_map_transitive_deps //target_mapping:use_lib_c
```

If we would use dependency `e`, the analysis would still fail as we mapped only `b` and its transitive dependencies.
Like with the direct dependency mapping, we simply could have mapped all direct and transitive of `a` into `a` itself to overcome such a case.
