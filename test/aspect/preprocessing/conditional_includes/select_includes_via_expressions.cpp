#define TOGGLE
#define SEVEN 7
#define ZERO 0

// Logical AND
#if defined(TOGGLE) && SEVEN > 5
#include "preprocessing/support/lib_a.h"
#else
#include "preprocessing/support/transitive.h"
#endif

// Logical OR where only the second operand is true
#if defined(UNDEFINED_MACRO) || SEVEN == 7
#include "preprocessing/support/lib_b.h"
#else
#include "preprocessing/support/transitive.h"
#endif

// Logical NOT applied to a value
#if !ZERO
#include "preprocessing/support/lib_c.h"
#else
#include "preprocessing/support/transitive.h"
#endif

// Ternary operator
#if (SEVEN > 10 ? 0 : 1)
#include "preprocessing/support/lib_d.h"
#else
#include "preprocessing/support/transitive.h"
#endif

// Arithmetic operators
#if (SEVEN * 2 + 1) % 5 == 0
#include "preprocessing/support/lib_e.h"
#else
#include "preprocessing/support/transitive.h"
#endif

// Bitwise operators
#if (SEVEN & 3) == 3
#include "preprocessing/support/lib_f.h"
#else
#include "preprocessing/support/transitive.h"
#endif

// Shift operators
#if (SEVEN << 1) == 14
#include "preprocessing/support/lib_g.h"
#else
#include "preprocessing/support/transitive.h"
#endif

// An identifier which is not a macro evaluates to 0
#if UNDEFINED_MACRO == 0
#include "preprocessing/support/lib_h.h"
#else
#include "preprocessing/support/transitive.h"
#endif

int main() {
    return libA() + libB() + libC() + libD() + libE() + libF() + libG() + libH();
}
