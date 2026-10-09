#define SQUARE(x) (x) * (x)
#define SQUARE_ALIAS SQUARE
#define STRINGIFY(x) #x

// The result of a function like macro can decide which file is included
#if SQUARE(5) > 10
#include "preprocessing/support/lib_a.h"
#else
#include "preprocessing/support/transitive.h"
#endif

// The result of a function like macro alias can decide which file is included
#if SQUARE_ALIAS(5) > 10
#include "preprocessing/support/lib_b.h"
#else
#include "preprocessing/support/transitive.h"
#endif

// The preprocessor operator '#' allows making string versions of provided input
// clang-format off
#include STRINGIFY(preprocessing/support/lib_c.h)
// clang-format on

int main() {
    return libA() + libB() + libC();
}
