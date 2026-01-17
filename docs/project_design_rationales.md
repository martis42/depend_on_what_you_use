# Noteworthy project design decisions

## Why use Boost Wave instead of preprocessor X

The decision was mostly based on [Boost Wave](https://github.com/boostorg/wave) being easy to integrate with Bazel and working for all our test cases.

We also looked into using the LLVM preprocessor.
Although a [LLVM Bazel setup](https://github.com/llvm/llvm-project/tree/main/utils/bazel) exists, it is experimental and lacking support at the time of writing this.

## Why use a multi step automatic fixes workflow

Having to execute a separate tool to apply fixes seems bothersome.
Ideally, DWYU would perform fixes while analyzing the problems.<br>
However, given DWYU is implemented as a Bazel aspect, there are limitations to what we can do in a single step:

- The DWYU aspect is analyzing the dependencies of the targets.
  Changing the dependencies while analyzing them would invalidate the dependency graph and require rebuilding the graph after each fix before continuing to analyze more targets.
  There is no standard feature of Bazel aspects allowing this.
- A Bazel aspect is executed in the sandbox.
  To be able to modify the BUILD files in the workspace, one would have to escape the sandbox.
  This is generally considered a bad practice when working with Bazel.

We circumvent the above problems by using a two step approach.
First we discover all problems and store the result in a machine readable format.
Then, we use a separate tool to process the results and apply fixes to the BUILD files in the workspace.
There are no problems regarding the sandboxing, since we utilize `bazel run` to execute the fixing tool.
A tool being executed like this can access any part of the host system.

# Rejected Concepts

## Includes parsing via .d files

Most modern compilers can generate `.d` files which document the headers required to compile a source file.
Essentially, this makes parsing of source code and aggregating the include statements with custom tooling superfluous.

One downside is, that this only works for source files, but not for header only code.
This could be mitigated by generating source files for the headers and then running the compiler on them.

A major drawback of this approach is however, that the `.d` files list all transitively included headers which are required for compiling a source file.

For example, given the 3 targets _A_, _B_ and _C_ with the files:

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
This makes sense, as the compiler requires all used headers to compile `c.cpp`.
However, it makes the `.d` file impractical for DWYU.
We need to know if header `a.h` was included directly in `c.cpp` or is used transitively by `b.h`.
Without this distinction we cannot compare the include statements to the list of direct dependencies.

At the time of writing this no way could be found to configure GCC to generate `.d` files matching our requirements.

## Using the Bazel CC toolchain preprocessor

Running our own preprocessing is slow and provides imperfect results.
On a first glance it seems like using the highly optimized CC toolchain preprocessor which is also used while you compile code might be a better choice.
Especially, given one can get information about the included headers from it by parsing the preprocessed output or by using the `-H` option with gcc or clang.
However, this approach has loop holes which can falsify the results due to how include guards work.

Assume we have the `BUILD` file

```starlark
cc_library(
  name = "transitive",
  hdrs = ["transitive.h"],
)

cc_library(
  name = "lib",
  hdrs = ["lib.h"],
  deps = ["//:transitive],
)

cc_binary(
  name = "main",
  srcs = ["main.cpp"],
  deps = ["//:lib"],
)
```

with these source files

`transitive.h`

```c++
#ifndef TRANSITIVE_H
#define TRANSITIVE_H

void doDetails() {}

#endif
```

`lib.h`

```c++
#ifndef TRANSITIVE_H
#define TRANSITIVE_H

#include "transitive.h"

void doSome() {
  doDetails();
}

void doOther() {}

#endif
```

`main.cpp`

```c++
#include "lib.h"
// This include violates the DWYU principles since the cc_binary target does not depend directly on //:transitive
#include "transitive.h"

int main() {
  doDetails();
  doOther();
  return 0
}
```

This basic example shows a violation of the principles enforced by DWYU.
However, this is invisible to the preprocessor.
The preprocessor will neither with the `-H` option (in case of gcc or clang) nor in its preprocessed output mention that `main.cpp` includes `transitive.h`.
This is due to `lib.h` including `transitive.h` itself.
After this the include guard of `transitive.h` is active and the second inclusion in `main.cpp` is ignored without any trace or warning about it being skipped.
Consequently, we are missing the information to report this problem.

## Preprocessing the complete source tree including all transitive includes down to system level

After realizing we [can't use the CC toolchain preprocessor](#using-the-bazel-cc-toolchain-preprocessor) we investigated finding a C/C++ preprocessor library.
While implementing prototypes for the new C++ based preprocessing step, we tried performing a full preprocessing, like the real compilation step does.
The approach to fully preprocess all transitive includes down to system level ans standard library headers failed, though.

To preprocess those low level headers, a lot of defines have to be set properly.
We don't know all the relevant defines and their correct value.
Even when fetching all defines known to the real compilation step by running it with `-dM` (assuming a gcc or clang toolchain) and forwarding those to our own preprocessing, we still encountered issues in system and standard library headers.

Performing preprocessing at all is already an edge case only relevant for projects using conditional preprocessor statements to control their include statements.
Many projects don't use conditional includes at all.<br>
Preprocessing all system and standard library headers would only be relevant if defines set in those low level headers are used in controlling conditional include statements in project or external code.
In other words, this is an edge case of an edge case.
Therefore, we consider DWYU not supporting this as acceptable.

Thus, DWYU ignores system and standard library headers and preprocesses only the workspace code and external dependencies.
Given the learnings we made, there are no plans to work on full preprocessing again.

Consequently, DWYU can only resolve conditional include statements based on macros defined in the workspace code or external dependencies.
If macros defined in system or toolchain headers are required to resolve conditional include statements, the user has to define those manually when invoking DWYU (e.g. via `--cxxopt`).
