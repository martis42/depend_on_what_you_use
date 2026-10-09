#define PASTE(a, b) a##b
#define PASTE_EXPANDED(a, b) PASTE(a, b)

#define PATH_A "preprocessing/support/lib_a.h"
#define PATH_D "preprocessing/support/lib_d.h"
#define PATH_OF(suffix) PATH_##suffix
#define SELECTED_SUFFIX D

#define FEATURE_B 1

#define IMPL_double(x) ((x) * 2)
#define APPLY(name, x) IMPL_##name(x)

// Pasting builds the name of the macro providing the include path
#include PATH_OF(A)

// Pasting builds the name of a macro used in a condition
#if PASTE(FEATURE_, B)
#include "preprocessing/support/lib_b.h"
#else
#include "preprocessing/support/transitive.h"
#endif

// Pasting builds a number
#if PASTE(1, 0) == 10
#include "preprocessing/support/lib_c.h"
#else
#include "preprocessing/support/transitive.h"
#endif

// Pasting after the expansion of macro arguments
#include PASTE_EXPANDED(PATH_, SELECTED_SUFFIX)

// Pasting builds the name of a function like macro
#if APPLY(double, 5) == 10
#include "preprocessing/support/lib_e.h"
#else
#include "preprocessing/support/transitive.h"
#endif

int main() {
    return libA() + libB() + libC() + libD() + libE();
}
