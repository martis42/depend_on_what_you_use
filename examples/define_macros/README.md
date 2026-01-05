By default, DWYU uses a preprocessor to parse the source files of the target under inspection.
This step is done to enable properly parsing conditional include statements based on some macro values.

This approach can fail if the macro is unknown to DWYU.
Some macros are defined compiler internally and not available to Bazel.
Others might be defined in system or CC toolchain headers, which are not analyzed by DWYU.

In such cases you can either:

- Deactivate preprocessing with the DWYU factory attribute `no_preprocessor`.
- Set the macros manually so make them available to DWYU

This example demonstrated the second option.

Executing the following shows you the failure occurring if some macros are unknown to the DWYU preprocessor.

```shell
bazel build --config=dwyu //define_macros:main
```

In the [bazelrc](/examples/.bazelrc) file we define config `dwyu_with_macros` which sets various macos explicitly whenever we run DWYU.
Executing the following demonstrates that this allows us to properly analyze the code.

```shell
bazel build --config=dwyu_with_macros //define_macros:main
```
