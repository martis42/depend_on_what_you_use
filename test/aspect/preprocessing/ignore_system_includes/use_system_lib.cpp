// Processing this header would make the switch known, which then causes including a header which causes a missing
// direct dependency finding. Thus, we can only analyze this file successfully if we ignore system includes.
#include <system_switch.h>

#include "preprocessing/support/lib_a.h"
#ifdef SYSTEM_SWITCH
// If we reach this line in preprocessing, this causes a missing direct dependency finding.
#include "preprocessing/support/transitive.h"
#endif

int main() {
    return 42;
}
