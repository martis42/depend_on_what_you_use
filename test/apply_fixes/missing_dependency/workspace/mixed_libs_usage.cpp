#include "mixed_libs_usage.h"
// used publicly and privately
#include "libs/foo.h"
// used solely privately
#include "libs/sub/bar.h"

int doMixed() {
    return doRoot() + doFoo() + doBar();
}
