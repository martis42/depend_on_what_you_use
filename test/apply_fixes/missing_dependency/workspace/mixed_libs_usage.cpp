#include "missing_dependency/workspace/mixed_libs_usage.h"
// used publicly and privately
#include "missing_dependency/workspace/libs/foo.h"
// used solely privately
#include "missing_dependency/workspace/libs/sub/bar.h"

int doMixed() {
    return doRoot() + doFoo() + doBar();
}
