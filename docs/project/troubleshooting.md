## Compiler errors

DWYU is developed with many active compiler warnings to make it unlikely that you see compiler warnings when using the DWYU tools with your C++ toolchain.
However, there are so many compiler warnings and compilers, that we can't guarantee this.

If you see compiler warnings related to DWYU or its transitive dependencies, you can silence them via [--per_file_copt](https://bazel.build/reference/command-line-reference#flag--per_file_copt) and [--host_per_file_copt](https://bazel.build/reference/command-line-reference#flag--host_per_file_copt).
For example if you see warnings coming from the `boost.wave` dependency, you could silence them like this in your `.bazelrc` file:

```bash
build --per_file_copt=boost.wave/src/.*@-w
build --host_per_file_copt=boost.wave/src/.*@-w
```
