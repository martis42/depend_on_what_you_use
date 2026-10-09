#define SELECTOR 2

// A later '#elif' is selected if the earlier conditions are false
#if SELECTOR == 1
#include "preprocessing/support/transitive.h"
#elif SELECTOR == 2
#include "preprocessing/support/lib_a.h"
#elif SELECTOR == 2
#include "preprocessing/support/transitive.h"
#else
#include "preprocessing/support/transitive.h"
#endif

// The '#else' is selected if all earlier conditions are false
#if SELECTOR == 1
#include "preprocessing/support/transitive.h"
#elif SELECTOR == 3
#include "preprocessing/support/transitive.h"
#else
#include "preprocessing/support/lib_b.h"
#endif

// Only the first true condition is selected
#if SELECTOR == 2
#include "preprocessing/support/lib_c.h"
#elif SELECTOR == 2
#include "preprocessing/support/transitive.h"
#else
#include "preprocessing/support/transitive.h"
#endif

// Nested conditional with true inner condition
#if SELECTOR == 2
#if SELECTOR > 1
#include "preprocessing/support/lib_d.h"
#else
#include "preprocessing/support/transitive.h"
#endif
#else
#include "preprocessing/support/transitive.h"
#endif

// Nested conditional with false inner condition
#if SELECTOR == 2
#if SELECTOR > 5
#include "preprocessing/support/transitive.h"
#else
#include "preprocessing/support/lib_e.h"
#endif
#endif

// A true inner condition does not matter if the outer condition is false
#if SELECTOR == 1
#if SELECTOR == 2
#include "preprocessing/support/transitive.h"
#endif
#else
#include "preprocessing/support/lib_f.h"
#endif

int main() {
    return libA() + libB() + libC() + libD() + libE() + libF();
}
