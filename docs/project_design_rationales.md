# Documentation of noteworthy project design decisions <!-- omit in toc -->

- [General](#general)
  - [Why use Python](#why-use-python)
  - [Why use a multi step automatic fixes workflow](#why-use-a-multi-step-automatic-fixes-workflow)
- [Rejected Concepts](#rejected-concepts)
  - [Includes parsing via .d files](#includes-parsing-via-d-files)

# General

## Why use Python

The project started with Python as it eased coming up with the first prototype.
Also, C++ has a quite limited standard library compared to Python and in the past not many Bazel ready c++ libraries were available.

Given, bzlmod made it far easier to depend on many established C++ dependencies and in general more things support Bazel nowadays, we might switch to a C++ implementation eventually.

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
