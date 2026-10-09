// Two headers with the same name are available. The first one forwards to the second one via '#include_next'.
#include <next_header.h>

// The first header is found
#ifdef FIRST_HEADER_PROCESSED
#include "preprocessing/support/lib_a.h"
#else
#include "preprocessing/support/transitive.h"
#endif

// The search of '#include_next' continues after the include path of the first header
#ifdef SECOND_HEADER_PROCESSED
#include "preprocessing/support/lib_b.h"
#else
#include "preprocessing/support/transitive.h"
#endif

// TODO DWYU cannot evaluate '__has_include_next', thus this case currently fails
//      Also uncomment the code in the support header 'include_next/first/next_header.h' and add the C++17 copts.
// '__has_include_next' finds the next header with the same name
// #ifdef FIRST_HEADER_SEES_NEXT
// #include "preprocessing/support/lib_c.h"
// #else
// #include "preprocessing/support/transitive.h"
// #endif

int main() {
    // TODO add libC() when '__has_include_next' is fixed
    return libA() + libB();
}
