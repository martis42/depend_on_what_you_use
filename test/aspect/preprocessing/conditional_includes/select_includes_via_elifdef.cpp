#define DEFINED_MACRO

// '#elifdef' is selected if the earlier conditions are false
#ifdef UNDEFINED_MACRO
#include "preprocessing/support/transitive.h"
#elifdef DEFINED_MACRO
#include "preprocessing/support/lib_a.h"
#else
#include "preprocessing/support/transitive.h"
#endif

// '#elifndef' is selected if the earlier conditions are false
#ifdef UNDEFINED_MACRO
#include "preprocessing/support/transitive.h"
#elifndef UNDEFINED_MACRO
#include "preprocessing/support/lib_b.h"
#else
#include "preprocessing/support/transitive.h"
#endif

// '#elifdef' is not evaluated if an earlier condition was true
#ifdef DEFINED_MACRO
#include "preprocessing/support/lib_c.h"
#elifdef DEFINED_MACRO
#include "preprocessing/support/transitive.h"
#endif

int main() {
    return libA() + libB() + libC();
}
