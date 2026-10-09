// Attribute support can be queried
#if __has_cpp_attribute(nodiscard)
#include "preprocessing/support/lib_a.h"
#else
#include "preprocessing/support/transitive.h"
#endif

// The existence of '__has_cpp_attribute' can be tested
#if defined(__has_cpp_attribute)
#include "preprocessing/support/lib_b.h"
#else
#include "preprocessing/support/transitive.h"
#endif

// An unknown attribute evaluates to 0
#if __has_cpp_attribute(attribute_which_does_not_exist)
#include "preprocessing/support/transitive.h"
#else
#include "preprocessing/support/lib_c.h"
#endif

// The result is a number which can be compared
#if __has_cpp_attribute(nodiscard) >= 201603L
#include "preprocessing/support/lib_d.h"
#else
#include "preprocessing/support/transitive.h"
#endif

int main() {
    return libA() + libB() + libC() + libD();
}
