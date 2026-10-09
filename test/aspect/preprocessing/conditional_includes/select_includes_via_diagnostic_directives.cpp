// An inactive '#error' does not abort the preprocessing
#ifdef UNDEFINED_MACRO
#error "This branch is not active"
#else
#include "preprocessing/support/lib_a.h"
#endif

// An inactive '#warning' is ignored
#ifdef UNDEFINED_MACRO
#warning "This branch is not active"
#else
#include "preprocessing/support/lib_b.h"
#endif

// An active '#warning' does not abort the preprocessing
#warning "This warning is expected"
#include "preprocessing/support/lib_c.h"

// Pragmas can be placed around includes
#pragma Some diagnostic push
#include "preprocessing/support/lib_d.h"
#pragma Some diagnostic pop

int main() {
    return libA() + libB() + libC() + libD();
}
