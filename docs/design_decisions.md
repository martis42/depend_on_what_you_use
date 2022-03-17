# Design Decisions

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
