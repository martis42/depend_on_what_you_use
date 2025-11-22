// Show we properly process macros coming from another file
#include "macros.h"

// One can use a define as indirection for the include path
#include LIB_A_FILE_PATH

// The existence of a define can decide if we include one file or another
#ifdef TOGGLE
#include "support/lib_b.h"
#else
// If this would be included, it would fail the DWYU analysis
#include "support/transitive.h"
#endif

// The value of a define can decide if we include one file or another
#if THE_ANSWER > 10
#include "support/lib_c.h"
#else
// If this would be included, it would fail the DWYU analysis
#include "support/transitive.h"
#endif

// The result of a function like macro can decide if we include one file or another
#if SQUARE(5) > 10
#include "support/lib_d.h"
#else
// If this would be included, it would fail the DWYU analysis
#include "support/transitive.h"
#endif

// The preprocessor operator '#' allows making string versions of provided input
// clang-format off
#include STRINGIFY(support/lib_e.h)
// clang-format off

int main() {
    return libA() + libB() + libC() + libD() + libE();
}
