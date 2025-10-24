// One can use a define as indirection for the include path
#include LIB_A_FILE_PATH

// The existence of a define can decide if we include one file or another
#ifdef TOGGLE
#include "support/lib_b.h"
#else
// If this would be included, it Would fail the DWYU analysis
#include "support/transitive.h"
#endif

// The value of a define can decide if we include one file or another
#if THE_ANSWER > 10
#include "support/lib_c.h"
#else
// If this would be included, it Would fail the DWYU analysis
#include "support/transitive.h"
#endif

int main() {
    return libA() + libB() + libC();
}
