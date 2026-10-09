#include "implementation_deps/use_defines.h"

// The value of a define can decide if we include one file or another
#if THE_ANSWER > 10
#include "support/lib_with_defines.h"
#else
#include "support/transitive.h"
#endif

int useDefines() {
    return libWitDefines() + 42;
}
