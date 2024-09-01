:warning: **Beware, this is an experimental feature which has not yet a stable behavior!**

`__cplusplus` is a macro defined by the compiler specifying if C++ is used to compile the file and which C++ standard is used.
`__cplusplus` typically is not passed on the compiler command line as defined value, but set internally by the preprocessor while processing a file.
Thus, DWYU does not know about it when performing the processing to resolve preprocessor statements.
To work around this, DWYU we can set `__cplusplus` based on a heuristic.

Executing <br>
`bazel build --aspects=//:aspect.bzl%dwyu_set_cplusplus --output_groups=dwyu //set_cpp_standard:cpp_lib` <br>
showcases that DWYU can process `__cplusplus` based preprocessor statements with a heuristic.

Executing <br>
`bazel build --aspects=//:aspect.bzl%dwyu_set_cplusplus --output_groups=dwyu //set_cpp_standard:use_specific_cpp_standard` <br>
showcases that checking for a specific C++ standard works as long as the compiler command specifies the desired C++ standard.
