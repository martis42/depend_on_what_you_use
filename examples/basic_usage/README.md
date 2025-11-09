Basic example showing correct and wrong dependency management and how DWYU reacts to those.

Executing DWYU on the correct target succeeds:

```shell
bazel build --config=dwyu //basic_usage:correct_dependencies
```

Executing DWYU on the target with faulty dependency management yields a failed build and an error message outlining the two problems of this target:

```shell
bazel build --config=dwyu //basic_usage:false_dependencies
```

DWYU can also report that the target under inspection is depending on something, it is not even using:

```shell
bazel build --config=dwyu //basic_usage:not_using_lib
```
