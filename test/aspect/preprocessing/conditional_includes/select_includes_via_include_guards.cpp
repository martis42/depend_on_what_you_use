// Each toggle header flips a flag macro whenever its content is processed

// A header with include guard is processed only once
#include "preprocessing/conditional_includes/support/guarded_toggle.h"
// The comment prevents clang-format from removing the duplicate include
#include "preprocessing/conditional_includes/support/guarded_toggle.h"
// GUARDED_FLAG is only defined if the include guard prevented the second inclusion
#ifdef GUARDED_FLAG
#include "preprocessing/support/lib_a.h"
#else
#include "preprocessing/support/transitive.h"
#endif

// A header with '#pragma once' is processed only once
#include "preprocessing/conditional_includes/support/pragma_once_toggle.h"
// Second inclusion
#include "preprocessing/conditional_includes/support/pragma_once_toggle.h"
// PRAGMA_ONCE_FLAG is only defined if pragma once prevented the second inclusion
#ifdef PRAGMA_ONCE_FLAG
#include "preprocessing/support/lib_b.h"
#else
#include "preprocessing/support/transitive.h"
#endif

// A header without protection is processed on every inclusion
#include "preprocessing/conditional_includes/support/unguarded_toggle.h"
// Second inclusion
#include "preprocessing/conditional_includes/support/unguarded_toggle.h"
#ifndef UNGUARDED_FLAG
#include "preprocessing/support/lib_c.h"
#else
#include "preprocessing/support/transitive.h"
#endif

// An unprotected header can be included repeatedly with different macro states
#define VARIANT_A
#include "preprocessing/conditional_includes/support/variant_macros.h"
#undef VARIANT_A
#define VARIANT_B
#include "preprocessing/conditional_includes/support/variant_macros.h"

#ifdef RESULT_A
#include "preprocessing/support/lib_d.h"
#else
#include "preprocessing/support/transitive.h"
#endif

#ifdef RESULT_B
#include "preprocessing/support/lib_e.h"
#else
#include "preprocessing/support/transitive.h"
#endif

// The include guard macro is defined after including the header
#ifdef PREPROCESSING_CONDITIONAL_INCLUDES_SUPPORT_GUARDED_TOGGLE_H
#include "preprocessing/support/lib_f.h"
#else
#include "preprocessing/support/transitive.h"
#endif

int main() {
    return libA() + libB() + libC() + libD() + libE() + libF();
}
