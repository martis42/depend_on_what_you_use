#ifndef MISSING_DEPENDENCY_WORKSPACE_LIBS_FOO_H
#define MISSING_DEPENDENCY_WORKSPACE_LIBS_FOO_H

// Show that multiple files 'foo.h' in the dependency graph are no issue
#include "missing_dependency/workspace/other_lib/foo.h"

int doFoo() {
    return doOtherFoo() + 1337;
}

#endif // MISSING_DEPENDENCY_WORKSPACE_LIBS_FOO_H
