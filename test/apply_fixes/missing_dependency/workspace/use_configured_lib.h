#ifndef MISSING_DEPENDENCY_WORKSPACE_USE_CONFIGURED_LIB_H
#define MISSING_DEPENDENCY_WORKSPACE_USE_CONFIGURED_LIB_H

#include "missing_dependency/workspace/ambiguous_lib/lib.h"
#include "missing_dependency/workspace/configured_lib/configured_deps.h"

int useConfiguredLib() {
    return doSomethingConfigured() + doSomething();
}

#endif // MISSING_DEPENDENCY_WORKSPACE_USE_CONFIGURED_LIB_H
