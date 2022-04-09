# Design Philosophy

Depend On What You Use (DWYU) has been inspired by [Include What You Use (IWYU)](https://github.com/include-what-you-use/include-what-you-use).
Essentially DWYU applies the idea behind IWYU to the relationship between include statements and dependencies.

DWYUs design philosophy: \
**A C++ target shall list all dependencies from which it is including header files.
Header files from transitive dependencies shall not be used.**

For example, target A depends on `cc_library` B. B depends on `cc_library` C.
A is allowed to include headers from target B.
A is however not allowed to use headers from C, unless it specifies C as direct dependency. \
This rule is not enforced by the compiler.
A using headers from C would compile, since all public headers from all direct and transitive dependencies are present in the sandbox and are part of the include path for compiling A.

Adhering to this design principle has several advantages:

- One is compliant to Bazels `cc_library` design [regarding include paths](https://bazel.build/reference/be/c-cpp#hdrs).
  Bazel is not yet able to enforce its include paths design.
  But this might change at any time.
- Bazel performs efficient incremental builds by analyzing the dependency tree of the targets and does only what is really required.
  A dependency tree modeling the C++ source code as close as possible enables Bazel to work most efficiently.
- Depending on transitive dependencies can cause unexpected build failures.
  Assume one of your dependencies X is dropping its transitive dependency Y.
  This should not influence your target as long as Xs interface is not changing.
  However, if you use headers from Y, your build will fail unexpectedly.
- While reading a BUILD file one sees at a glance all other targets directly influencing the content of the BUILD file without having to read the source code.
- When analyzing the direct downstream dependencies of `cc_library` X (e.g. with bazel query) one can be sure that all places where Xs headers are used are discoverable through the Bazel dependency tree.
