#include "preprocessing/conditional_includes/select_includes_via_dep_defines.h"
#include "preprocessing/conditional_includes/support/lib_exporting_defines_a.h"

// Defines of a dependency are exported to the targets depending on it
#ifdef DEP_EXPORTED_DEFINE
#include "preprocessing/support/lib_a.h"
#else
#include "preprocessing/support/transitive.h"
#endif

// Defines with a value are exported to the targets depending on it
#if DEP_EXPORTED_VALUE == 42
#include "preprocessing/support/lib_b.h"
#else
#include "preprocessing/support/transitive.h"
#endif

// Defines of a transitive dependency are exported as well
#ifdef DEP_TRANSITIVE_DEFINE_A
#include "preprocessing/support/lib_c.h"
#else
#include "preprocessing/support/transitive.h"
#endif

// Defines of a transitive dependency are exported, but this chain is broken by using implementation_deps
#ifndef DEP_TRANSITIVE_DEFINE_B
#include "preprocessing/support/lib_d.h"
#else
#include "preprocessing/support/transitive.h"
#endif

// Local defines of a dependency are not exported
#ifndef DEP_LOCAL_DEFINE
#include "preprocessing/support/lib_e.h"
#else
#include "preprocessing/support/transitive.h"
#endif

int doSth() {
    return libA() + libB() + libC() + libD();
}
