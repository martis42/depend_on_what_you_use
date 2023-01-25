Using relative include paths is considered a bad practice in Bazel projects as documented in [bazel-and-cpp](https://bazel.build/docs/bazel-and-cpp#include-paths).
However, since relative include paths are a valid C++ feature, DWYU aims to support this.
