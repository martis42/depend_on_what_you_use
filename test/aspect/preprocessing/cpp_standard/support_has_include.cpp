// If __has_include cannot be parsed, we won't include the header causing unused dependency finding
#if __has_include("preprocessing/support/lib_a.h")
#include "preprocessing/support/lib_a.h"
#endif

// Ensure _has_include is not just always true, as otherwise we include a transitive header causing a DWYU finding
#if !__has_include("preprocessing/support/lib_a.h")
#include "preprocessing/support/transitive.h"
#endif

// Ensure the preprocessor parses __has_include without breaking down, otherwise this include is not reached causing an unused dependency finding
#include "preprocessing/support/lib_b.h"

int main() {
    return 0;
}
