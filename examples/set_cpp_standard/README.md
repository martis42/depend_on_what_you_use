:warning: **Beware, this is a DEPRECATED feature which will be removed in the next release!** :warning:<br>
See the [define_macros](/examples/define_macros/) example for the forward path solution.

`__cplusplus` is a macro defined by the compiler specifying if C++ is used to compile the file and which C++ standard is used.
`__cplusplus` typically is not passed on the compiler command line as defined value, but set internally by the preprocessor while processing a file.
Thus, DWYU does not know about it when performing the processing to resolve preprocessor statements.
To work around this, DWYU we can set `__cplusplus` based on a heuristic.

Executing the following showcases that checking for a specific C++ standard works as long as the compiler command specifies the desired C++ standard.
We specify `-std=..` here explicitly for demonstration purposes.
Most toolchains set this value automatically and DWYU picks it up.

```shell
bazel build --config=dwyu_set_cplusplus //set_cpp_standard:use_specific_cpp_standard
```
