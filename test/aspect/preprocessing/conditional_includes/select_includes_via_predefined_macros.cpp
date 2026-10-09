#include "preprocessing/conditional_includes/support/include_level.h"

// The line number of the current position is available. Adapt the number if the lines above change.
#if __LINE__ == 4
#include "preprocessing/support/lib_a.h"
#else
#include "preprocessing/support/transitive.h"
#endif

// The main file has the include level 0
#if __INCLUDE_LEVEL__ == 0
#include "preprocessing/support/lib_b.h"
#else
#include "preprocessing/support/transitive.h"
#endif

// A file included from the main file has the include level 1
#ifdef INCLUDE_LEVEL_ONE
#include "preprocessing/support/lib_c.h"
#else
#include "preprocessing/support/transitive.h"
#endif

int main() {
    return libA() + libB() + libC();
}
