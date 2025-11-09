#include "define_macros/lib.h"

// If FOO is not defined, this will fail the DWYU analysis due to using the header from a transitive dependency
#ifndef FOO
#include "define_macros/transitive_dep_a.h"
#endif

// If the C++ standard is not known, this will fail the DWYU analysis due to using the header from a transitive
// dependency
#if __cplusplus < 199711
#include "define_macros/transitive_dep_b.h"
#endif

int main() {
    return 0;
}
