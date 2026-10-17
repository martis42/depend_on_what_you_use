DWYU uses a preprocessing step to parse the source files of the target under inspection.
By default this is a simple text parsing extracting include statements.
If a project is using conditional include statements based on `#ifdef` and similar preprocessor logic one has to choose a different DWYU preprocessing mode with DWYU aspect option `preprocessing_mode`.

The more complex `preprocessing_mode` modes performing a "real" preprocessing can still fail fail if a macro is unknown to DWYU.
Some macros are defined compiler internally and not available to Bazel.
Others might be defined in system or CC toolchain headers, which are not analyzed by DWYU.

In such cases you can set the macros manually so make them available to DWYU
This example demonstrates this.

Executing the following shows you the failure occurring if some macros are unknown to the DWYU preprocessing step.

```shell
bazel build --config=dwyu //define_macros:main
```

In the [bazelrc](/examples/.bazelrc) file we define config `dwyu_with_macros` which sets various macos explicitly whenever we run DWYU.
Also, we tell DWYU to use a more complex preprocessing strategy which behaves similar to a real preprocessor.
Executing the following demonstrates that this allows us to properly analyze the code.

```shell
bazel build --config=dwyu_with_macros //define_macros:main
```
