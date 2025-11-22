#include "dir/ext_lib_with_includes.h"
#include "ext_lib.h"
#include "ext_lib_with_strip_prefix.h"
#include "some/prefix/ext/dir/ext_lib_with_add_prefix.h"

int doSomethingWithExternal() {
    return extLib() + extLibwithIncludes() + extLibwithStripPrefix() + extLibwithAddPrefix();
}
