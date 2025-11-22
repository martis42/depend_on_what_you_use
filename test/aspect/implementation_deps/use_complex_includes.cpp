#include "dir/lib_with_includes.h"
#include "lib_with_strip_prefix.h"
#include "some/prefix/sub/dir/lib_with_add_prefix.h"

int doSomethingWithComplexIncludes() {
    return libwithIncludes() + libwithStripPrefix() + libwithAddPrefix();
}
