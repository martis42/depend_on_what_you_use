// '#undef' removes a macro
#define UNDEFINED_BY_SOURCE
#undef UNDEFINED_BY_SOURCE
#ifndef UNDEFINED_BY_SOURCE
#include "preprocessing/support/lib_a.h"
#else
#include "preprocessing/support/transitive.h"
#endif

// A macro can be redefined with a new value after '#undef'
#define REDEFINED_VALUE 1
#undef REDEFINED_VALUE
#define REDEFINED_VALUE 2
#if REDEFINED_VALUE == 2
#include "preprocessing/support/lib_b.h"
#else
#include "preprocessing/support/transitive.h"
#endif

// A macro defined in an active branch is visible afterwards
#if 1
#define DEFINED_IN_ACTIVE_BRANCH
#endif
#ifdef DEFINED_IN_ACTIVE_BRANCH
#include "preprocessing/support/lib_c.h"
#else
#include "preprocessing/support/transitive.h"
#endif

// A macro defined in an inactive branch does not exist
#if 0
#define DEFINED_IN_INACTIVE_BRANCH
#endif
#ifndef DEFINED_IN_INACTIVE_BRANCH
#include "preprocessing/support/lib_d.h"
#else
#include "preprocessing/support/transitive.h"
#endif

int main() {
    return libA() + libB() + libC() + libD();
}
