// Whitespace is allowed between
// clang-format off
#   include     "preprocessing/support/lib_a.h"
// clang-format on

// Comments can be placed around the elements of an include directive
// clang-format off
#include /* comment */ "preprocessing/support/lib_b.h" // comment
// clang-format on

// Includes in comments are ignored

// #include "preprocessing/support/transitive.h"
/*
#include "preprocessing/support/transitive.h"
*/
/* /* /*
#include "preprocessing/support/transitive.h"
*/
/*
// #include "preprocessing/support/transitive.h"
*/

// Ensure we reach this and preprocessor did not break down before this include
#include "preprocessing/support/lib_c.h"

int main() {
    return libA() + libB() + libC();
}
