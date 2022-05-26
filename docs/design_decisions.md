# Design Decisions <!-- omit in toc -->

- [Design: Why use a multi step automatic fixes workflow](#design-why-use-a-multi-step-automatic-fixes-workflow)
- [Rejected: Includes parsing via .d files](#rejected-includes-parsing-via-d-files)
- [Platforms: Why is Bazel < 4.0.0 not supported](#platforms-why-is-bazel--400-not-supported)
- [Platforms: Why is Python < 3.6 not supported](#platforms-why-is-python--36-not-supported)

## Design: Why use a multi step automatic fixes workflow

Having to execute a separate tool to apply fixes seems bothersome. Ideally, DWYU would perform fixes
while analyzing the problems.<br/>
However, given DWYU is implemented as a Bazel aspect, there are limitations to what we can do in a single step:
- The DWYU aspect is analyzing the dependencies of the targets. Changing the dependencies while analyzing them would
  invalidate the dependency graph and require rebuilding the graph after each fix before continuing to
  analyze more targets. There is no standard feature of Bazel aspects allowing this.
- A Bazel aspect is executed in the sandbox. To be able to modify the BUILD files in the workspace, one would have to
  escape the sandbox. This is generally considered a bad practice when working with Bazel.

We circumvent the above problems by using a two step approach. First we discover all problems and store the result in
a machine readable format. Then, we use a separate tool to process the results and apply fixes to the BUILD files in
the workspace. There are no problems regarding the sandboxing, since we utilize `bazel run` to execute the fixing tool.
A tool being executed like this can access any part of the host system.

## Rejected: Includes parsing via .d files

Most modern compilers can generate `.d` files which document the headers required to compile a source file.
Essentially, this makes parsing of source code and aggregating the include statements with custom tooling superfluous.

One downside is, that this only works for source files, but not for header only code.
This could be mitigated by generating source files for the headers and then running the compiler on them.

A major drawback of this approach is however, that the `.d` files list all transitively included headers which are
required for compiling a source file.

For example, given the 3 target `A`, `B` and `C` with the files:

`a.h`
```c++
void doA() { ... };
```

`b.h`
```c++
#include "a.h"

void doB() { doA(); };
```

`c.cpp`
```c++
#include "b.h"

void doC() { doB(); };
```

The `.d` file for `c.cpp` will list the headers `a.h` and `b.h`.
This makes sense, after all the compiler requires all used headers to compile `c.cpp`.
However, it makes the `.d` file impractical for DWYU.
We need to know if header `a.h` was included directly in `c.cpp` or is used transitively by `b.h`.
Without this distinction we cannot compare the include statements to the list of direct dependencies.

## Platforms: Why is Bazel < 4.0.0 not supported

The aspect implementation is not compatible to old Bazel versions due to:
- Before 3.3.0 `CcInfo` compilation_context has a structure which is not supported by the aspect
- Before 4.0.0 the global `json` module is not available in Starlark

## Platforms: Why is Python < 3.6 not supported

As a rule of thumb, we aim to only support Python versions which are not EOL. Using a modern Python version enables
us to write clean code utilizing modern Python features.

Nevertheless, we support Python 3.6 although it is already EOL. This version is the default for Ubuntu 18.04, which
a lot of users are still using. Thus, we make an exception for Python 3.6.

We are not making this exception for even older versions. Especially given we make extensive use of the features
_formatting string literals_ and _type annotations_, which are at not available in older versions.
