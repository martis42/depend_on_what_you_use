#include "implementation_deps/use_defines.h"

// The value of a define can decide if we include one file or another
#if THE_ANSWER > 10
#include "support/lib_with_defines.h"
#else
// If this would be included, it would fail the DWYU analysis
#include "support/transitive.h"
#endif

int useDefines() {
    return libWitDefines() + 42;
}
