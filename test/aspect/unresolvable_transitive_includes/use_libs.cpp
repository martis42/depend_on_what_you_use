// The own header has to come first. It pulls in a header subtree containing include statements which the
// preprocessing cannot resolve. This must not corrupt discovering the include statements coming afterwards.
#include "unresolvable_transitive_includes/use_libs.h"

#include "unresolvable_transitive_includes/support/impl_dep.h"

int useLibs() {
    return wrapHeavy() + implDep() + 11;
}
