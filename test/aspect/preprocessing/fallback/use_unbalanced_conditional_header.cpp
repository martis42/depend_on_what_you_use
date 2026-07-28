// The included header ends inside an open conditional block. boost::wave leaks this conditional into this file and
// skips the include statement below. The fallback to lexically scanning the file ensures it is still found.
#include "preprocessing/fallback/lib_ending_inside_conditional.h"

#include "preprocessing/fallback/lib_used_after_problematic_construct.h"

int main() {
    return usedAfterProblematicConstruct();
}
