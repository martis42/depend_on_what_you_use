#ifndef MISSING_DEPENDENCY_WORKSPACE_MIXED_LIBS_USAGE_H
#define MISSING_DEPENDENCY_WORKSPACE_MIXED_LIBS_USAGE_H

// used solely publicly
#include "missing_dependency/workspace/root_lib.h"
// used publicly and privately
#include "missing_dependency/workspace/libs/foo.h"

int doMixed();

#endif // MISSING_DEPENDENCY_WORKSPACE_MIXED_LIBS_USAGE_H
