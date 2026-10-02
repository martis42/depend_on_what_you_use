#include "preprocessing/fallback/variadic_macro.h"

// Invoking a variadic macro without variadic arguments makes boost::wave raise a warning and stop processing the
// rest of the file. The fallback to lexically scanning the file ensures the include statement below is still found.
DWYU_TEST_LOG("some message")

#include "preprocessing/fallback/lib_used_after_problematic_construct.h"

int main() {
    return usedAfterProblematicConstruct();
}
