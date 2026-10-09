// One can use a define as indirection for the include path
#include LIB_A_FILE_PATH

// The existence of a define can decide if we include one file or another
#ifdef TOGGLE
#include "preprocessing/support/lib_b.h"
#else
#include "preprocessing/support/transitive.h"
#endif

// The value of a define can decide if we include one file or another
#if THE_ANSWER > 10
#include "preprocessing/support/lib_c.h"
#else
#include "preprocessing/support/transitive.h"
#endif

// A macro defined without value has the value 1
#if DEFAULT_VALUE_MACRO == 1
#include "preprocessing/support/lib_d.h"
#else
#include "preprocessing/support/transitive.h"
#endif

// A function like macro can be defined
#if SQUARE_FROM_BUILD(5) > 10
#include "preprocessing/support/lib_e.h"
#else
#include "preprocessing/support/transitive.h"
#endif

int main() {
    return libA() + libB() + libC() + libD() + libE();
}
