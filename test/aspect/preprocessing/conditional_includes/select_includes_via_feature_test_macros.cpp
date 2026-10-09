// Language feature test macro with value
#if __cpp_concepts >= 201907L
#include "preprocessing/support/lib_a.h"
#else
#include "preprocessing/support/transitive.h"
#endif

// Language feature test macro from an older standard
#ifdef __cpp_if_constexpr
#include "preprocessing/support/lib_b.h"
#else
#include "preprocessing/support/transitive.h"
#endif

// Language feature test macro from a newer standard
#ifndef __cpp_pack_indexing
#include "preprocessing/support/lib_c.h"
#else
#include "preprocessing/support/transitive.h"
#endif

int main() {
    return libA() + libB() + libC();
}
