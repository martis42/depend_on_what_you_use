#include "preprocessing/conditional_includes/support/lib_with_macros.h"

// Macros defined by a header of a dependency
#ifdef DEP_HEADER_MACRO
#include "preprocessing/support/lib_a.h"
#else
#include "preprocessing/support/transitive.h"
#endif

// Macros of a dependency header can depend on defines of the including target
#ifdef DEP_HEADER_CONDITIONAL_MACRO
#include "preprocessing/support/lib_b.h"
#else
#include "preprocessing/support/transitive.h"
#endif

// The include path is provided by a macro from a dependency header
#include DEP_HEADER_LIB_PATH

// Macros defined by a header which is included by a header of the dependency
#ifdef DEP_NESTED_MACRO
#include "preprocessing/support/lib_d.h"
#else
#include "preprocessing/support/transitive.h"
#endif

int main() {
    return libA() + libB() + libC() + libD();
}
