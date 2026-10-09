#define DEFINED_MACRO
#define ZERO_VALUE_MACRO 0

// '#ifndef' is true for undefined macros
#ifndef UNDEFINED_MACRO
#include "preprocessing/support/lib_a.h"
#else
#include "preprocessing/support/transitive.h"
#endif

// 'defined()' with parentheses
#if defined(DEFINED_MACRO)
#include "preprocessing/support/lib_b.h"
#else
#include "preprocessing/support/transitive.h"
#endif

// Negated 'defined()'
#if !defined(UNDEFINED_MACRO)
#include "preprocessing/support/lib_c.h"
#else
#include "preprocessing/support/transitive.h"
#endif

// 'defined' without parentheses
#if defined DEFINED_MACRO
#include "preprocessing/support/lib_d.h"
#else
#include "preprocessing/support/transitive.h"
#endif

// A macro defined with the value 0 is still defined
#ifdef ZERO_VALUE_MACRO
#include "preprocessing/support/lib_e.h"
#else
#include "preprocessing/support/transitive.h"
#endif

// Literal conditions
#if 0
#include "preprocessing/support/transitive.h"
#else
#include "preprocessing/support/lib_f.h"
#endif

int main() {
    return libA() + libB() + libC() + libD() + libE() + libF();
}
