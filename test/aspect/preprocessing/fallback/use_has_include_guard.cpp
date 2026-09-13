// '__has_include' is valid since C++17, but cannot be evaluated by boost::wave in our C++11 language mode. The
// fallback to lexically scanning the file ensures the guarded include statement is still found.
#if __has_include("preprocessing/fallback/lib_guarded_by_has_include.h")
#include "preprocessing/fallback/lib_guarded_by_has_include.h"
#endif

#include "preprocessing/fallback/lib_used_after_problematic_construct.h"

int main() {
    return guardedByHasInclude() + usedAfterProblematicConstruct();
}
