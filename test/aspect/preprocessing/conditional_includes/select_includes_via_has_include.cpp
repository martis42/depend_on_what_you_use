// If __has_include cannot be parsed, we won't include the header causing unused dependency finding
#if __has_include("preprocessing/support/lib_a.h")
#include "preprocessing/support/lib_a.h"
#endif

// Ensure __has_include is not just always true, as otherwise we include a transitive header causing a DWYU finding
#if !__has_include("preprocessing/support/lib_a.h")
#include "preprocessing/support/transitive.h"
#endif

// Angle bracket form
#if __has_include(<angle_lib_a.h>)
#include <angle_lib_a.h>
#else
#include "preprocessing/support/transitive.h"
#endif

// The argument can be provided by a macro
#define LIB_C_PATH "preprocessing/support/lib_c.h"
#if __has_include(LIB_C_PATH)
#include "preprocessing/support/lib_c.h"
#else
#include "preprocessing/support/transitive.h"
#endif

// The existence of '__has_include' can be tested
#if defined(__has_include)
#include "preprocessing/support/lib_d.h"
#else
#include "preprocessing/support/transitive.h"
#endif

// Combination with other operators
#if __has_include("preprocessing/support/lib_e.h") && !__has_include("preprocessing/support/not_existing.h")
#include "preprocessing/support/lib_e.h"
#else
#include "preprocessing/support/transitive.h"
#endif

// A header which does not exist
#if __has_include("preprocessing/support/not_existing.h")
#include "preprocessing/support/transitive.h"
#else
#include "preprocessing/support/lib_f.h"
#endif

// Usage in '#elif'
#if !__has_include("preprocessing/support/lib_g.h")
#include "preprocessing/support/transitive.h"
#elif __has_include("preprocessing/support/lib_g.h")
#include "preprocessing/support/lib_g.h"
#endif

// Ensure the preprocessor parses __has_include without breaking down, otherwise this include is not reached causing an unused dependency finding
#include "preprocessing/support/lib_b.h"

int main() {
    return libA() + libB() + libC() + libD() + libE() + libF() + libG();
}
