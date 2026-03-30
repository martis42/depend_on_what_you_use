// Include created via 'includes = []'
#include <includes.h>

// Paths created via 'include_prefix' and/or 'strip_include_prefix'
#include "foo/bar/sub_3.h"
#include "foo/bar/virtual_1.h"
#include "sub_1.h"

// Show one can still use the workspace path for including, even if virtual includes are used by the dependency
#include "missing_dependency/workspace/virtual_includes/sub/sub_2.h"
#include "missing_dependency/workspace/virtual_includes/virtual_2.h"

int main() {
    return doIncludes() + doVirtual1() + doVirtual2() + doSub1() + doSub2() + doSub3();
}
