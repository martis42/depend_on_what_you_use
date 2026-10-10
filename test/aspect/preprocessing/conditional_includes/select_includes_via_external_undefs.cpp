// A macro defined and undefined again via the build configuration does not exist
#ifndef CMDLINE_UNDEFINED
#include "preprocessing/support/lib_a.h"
#else
#include "preprocessing/support/transitive.h"
#endif

// The source file can override a macro defined via the build configuration
#undef CMDLINE_OVERRIDDEN
#define CMDLINE_OVERRIDDEN 2
#if CMDLINE_OVERRIDDEN == 2
#include "preprocessing/support/lib_b.h"
#else
#include "preprocessing/support/transitive.h"
#endif

int main() {
    return libA() + libB();
}
