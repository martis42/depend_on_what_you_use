Defines can influence which include statements are relevant.

These tests concentrate on parsing single files based on defines:

- specified in the parsed file itself
- coming from the C/C++ toolchain
- defined by the Bazel target attributes `defines`, `local_defines` or `cops`

Defines can also be imported into a file via an included header which specifies a define.
This use case is not yet supported.
We might add it at a later stage.
